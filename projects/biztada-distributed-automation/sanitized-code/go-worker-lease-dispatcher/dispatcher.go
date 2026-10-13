package dispatcher

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/redis/go-redis/v9"
)

// Task represents an incoming job message from Redis Streams
type Task struct {
	ID        string                 `json:"id"`
	AccountID string                 `json:"account_id"`
	Type      string                 `json:"type"`
	Payload   map[string]interface{} `json:"payload"`
}

// TaskHandler is the execution signature invoked when a task is leased
type TaskHandler func(ctx context.Context, task Task) error

// Dispatcher coordinates stream consumption, worker leasing, and heartbeat renewal
type Dispatcher struct {
	redisClient  *redis.Client
	leaseManager *LeaseManager
	streamName   string
	groupName    string
	consumerName string
	handler      TaskHandler
	wg           sync.WaitGroup
}

// NewDispatcher initializes a task consumer dispatcher
func NewDispatcher(
	client *redis.Client,
	streamName, groupName, consumerName string,
	handler TaskHandler,
) *Dispatcher {
	return &Dispatcher{
		redisClient:  client,
		leaseManager: NewLeaseManager(client),
		streamName:   streamName,
		groupName:    groupName,
		consumerName: consumerName,
		handler:      handler,
	}
}

// EnsureConsumerGroup creates the Redis stream consumer group if it does not exist
func (d *Dispatcher) EnsureConsumerGroup(ctx context.Context) error {
	err := d.redisClient.XGroupCreateMkStream(ctx, d.streamName, d.groupName, "$").Err()
	if err != nil && err.Error() != "BUSYGROUP Consumer Group name already exists" {
		return fmt.Errorf("failed to create consumer group: %w", err)
	}
	return nil
}

// Start runs the dispatch consumer loop until ctx is cancelled
func (d *Dispatcher) Start(ctx context.Context) {
	d.wg.Add(1)
	defer d.wg.Done()

	log.Printf("[Dispatcher %s] Started consuming from stream %s (group: %s)", d.consumerName, d.streamName, d.groupName)

	for {
		select {
		case <-ctx.Done():
			log.Printf("[Dispatcher %s] Shutdown signal received, terminating loop", d.consumerName)
			return
		default:
			// Read 1 task with a block timeout of 2 seconds
			entries, err := d.redisClient.XReadGroup(ctx, &redis.XReadGroupArgs{
				Group:    d.groupName,
				Consumer: d.consumerName,
				Streams:  []string{d.streamName, ">"},
				Count:    1,
				Block:    2 * time.Second,
			}).Result()

			if err != nil {
				if err == redis.Nil || ctx.Err() != nil {
					continue
				}
				log.Printf("[Dispatcher %s] Error reading from stream: %v", d.consumerName, err)
				time.Sleep(1 * time.Second)
				continue
			}

			if len(entries) == 0 || len(entries[0].Messages) == 0 {
				continue
			}

			msg := entries[0].Messages[0]
			d.processMessage(ctx, msg)
		}
	}
}

// processMessage attempts to acquire a lease on the task account, executes handler, and sends ACK
func (d *Dispatcher) processMessage(ctx context.Context, msg redis.XMessage) {
	rawPayload, ok := msg.Values["payload"].(string)
	if !ok {
		log.Printf("[Dispatcher] Invalid message payload structure for msg %s, acknowledging to drop", msg.ID)
		_ = d.redisClient.XAck(ctx, d.streamName, d.groupName, msg.ID).Err()
		return
	}

	var task Task
	if err := json.Unmarshal([]byte(rawPayload), &task); err != nil {
		log.Printf("[Dispatcher] JSON unmarshal failed for msg %s: %v", msg.ID, err)
		_ = d.redisClient.XAck(ctx, d.streamName, d.groupName, msg.ID).Err()
		return
	}

	leaseResource := fmt.Sprintf("account:%s", task.AccountID)
	leaseTTL := 60 * time.Second

	// Step 1: Acquire Distributed Lease
	acquired, err := d.leaseManager.Acquire(ctx, leaseResource, d.consumerName, leaseTTL)
	if err != nil || !acquired {
		log.Printf("[Dispatcher] Lease acquisition failed for account %s: %v (deferred)", task.AccountID, err)
		// Leave message in PEL so another worker or auto-claim sweeper can re-process
		return
	}

	// Step 2: Spawn background heartbeat routine
	taskCtx, cancel := context.WithCancel(ctx)
	defer cancel()

	heartbeatTicker := time.NewTicker(20 * time.Second)
	defer heartbeatTicker.Stop()

	go func() {
		for {
			select {
			case <-taskCtx.Done():
				return
			case <-heartbeatTicker.C:
				if err := d.leaseManager.Renew(context.Background(), leaseResource, d.consumerName, leaseTTL); err != nil {
					log.Printf("[Dispatcher] Warning: Failed to renew lease for %s: %v", leaseResource, err)
					cancel()
					return
				}
			}
		}
	}()

	// Step 3: Execute Business Logic Handler
	log.Printf("[Dispatcher] Executing task %s (type: %s) for account %s", task.ID, task.Type, task.AccountID)
	execErr := d.handler(taskCtx, task)

	// Step 4: Release Lease & Acknowledge Message
	_ = d.leaseManager.Release(context.Background(), leaseResource, d.consumerName)

	if execErr == nil {
		if ackErr := d.redisClient.XAck(ctx, d.streamName, d.groupName, msg.ID).Err(); ackErr != nil {
			log.Printf("[Dispatcher] Failed to acknowledge task %s: %v", task.ID, ackErr)
		} else {
			log.Printf("[Dispatcher] Task %s completed successfully and acknowledged", task.ID)
		}
	} else {
		log.Printf("[Dispatcher] Task %s failed execution: %v (leaving for retry)", task.ID, execErr)
	}
}

// Stop waits for in-flight tasks to terminate
func (d *Dispatcher) Stop() {
	d.wg.Wait()
}
