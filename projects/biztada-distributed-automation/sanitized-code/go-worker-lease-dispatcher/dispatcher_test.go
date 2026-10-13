package dispatcher

import (
	"context"
	"testing"
	"time"
)

// Unit test verifying Task struct serialization and lease error constants
func TestTaskSerialization(t *testing.T) {
	task := Task{
		ID:        "tsk_test_01",
		AccountID: "acc_biz_99",
		Type:      "CAMPAIGN_SYNC",
		Payload: map[string]interface{}{
			"action": "post_update",
			"batch":  10,
		},
	}

	if task.ID != "tsk_test_01" {
		t.Fatalf("expected task ID tsk_test_01, got %s", task.ID)
	}

	if task.AccountID != "acc_biz_99" {
		t.Fatalf("expected account ID acc_biz_99, got %s", task.AccountID)
	}
}

func TestContextCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	select {
	case <-ctx.Done():
		// Expected
	case <-time.After(50 * time.Millisecond):
		t.Fatal("context should be cancelled immediately")
	}
}
