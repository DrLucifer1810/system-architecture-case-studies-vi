package dispatcher

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

var (
	ErrLeaseAcquisitionFailed = errors.New("lease already held by another worker")
	ErrLeaseExpiredOrNotOwned  = errors.New("lease expired or not owned by caller")
)

// Lua script to atomically extend lock expiration only if the value matches the owner token
const renewLeaseLua = `
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("expire", KEYS[1], ARGV[2])
else
    return 0
end
`

// Lua script to atomically release lock only if the value matches the owner token
const releaseLeaseLua = `
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
`

// LeaseManager coordinates distributed locks with TTL heartbeats
type LeaseManager struct {
	client       *redis.Client
	renewScript  *redis.Script
	releaseScript *redis.Script
}

// NewLeaseManager creates a new instance of LeaseManager
func NewLeaseManager(client *redis.Client) *LeaseManager {
	return &LeaseManager{
		client:        client,
		renewScript:   redis.NewScript(renewLeaseLua),
		releaseScript: redis.NewScript(releaseLeaseLua),
	}
}

// Acquire attempts to acquire a lease for resourceKey with an ownerToken and TTL
func (lm *LeaseManager) Acquire(ctx context.Context, resourceKey string, ownerToken string, ttl time.Duration) (bool, error) {
	key := fmt.Sprintf("lock:%s", resourceKey)
	acquired, err := lm.client.SetNX(ctx, key, ownerToken, ttl).Result()
	if err != nil {
		return false, fmt.Errorf("failed to acquire lease: %w", err)
	}
	return acquired, nil
}

// Renew attempts to renew the lease expiration atomically
func (lm *LeaseManager) Renew(ctx context.Context, resourceKey string, ownerToken string, ttl time.Duration) error {
	key := fmt.Sprintf("lock:%s", resourceKey)
	res, err := lm.renewScript.Run(ctx, lm.client, []string{key}, ownerToken, int(ttl.Seconds())).Int()
	if err != nil {
		return fmt.Errorf("error running renew script: %w", err)
	}
	if res == 0 {
		return ErrLeaseExpiredOrNotOwned
	}
	return nil
}

// Release releases the lease if still held by ownerToken
func (lm *LeaseManager) Release(ctx context.Context, resourceKey string, ownerToken string) error {
	key := fmt.Sprintf("lock:%s", resourceKey)
	res, err := lm.releaseScript.Run(ctx, lm.client, []string{key}, ownerToken).Int()
	if err != nil {
		return fmt.Errorf("error running release script: %w", err)
	}
	if res == 0 {
		return ErrLeaseExpiredOrNotOwned
	}
	return nil
}
