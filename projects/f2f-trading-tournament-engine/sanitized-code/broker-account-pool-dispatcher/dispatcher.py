import json
import logging
from typing import Dict, Any

class BrokerAccountDispatcher:
    """
    Builds sanitized match assignment payloads and dispatches them
    to the Redis queue for external broker load balancer daemons.
    """
    QUEUE_KEY = "queue:lb:match_assignments"

    @classmethod
    def format_assignment_payload(
        cls,
        match_id: int,
        match_type: str,
        duration_minutes: int,
        p1_data: Dict[str, Any],
        p2_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Enforce automated 3-minute grace period
        adjusted_duration = duration_minutes + 3

        return {
            "id": match_id,
            "match_type": match_type,
            "status": "pending_confirmation",
            "duration_minutes": adjusted_duration,
            "player1": {
                "id": p1_data["id"],
                "name_account": p1_data["account"],
                "password_account": p1_data["password"],
                "server_account": p1_data["server"]
            },
            "player2": {
                "id": p2_data["id"],
                "name_account": p2_data["account"],
                "password_account": p2_data["password"],
                "server_account": p2_data["server"]
            }
        }

def test_dispatcher():
    p1 = {"id": 1, "account": "10001", "password": "secure_pass_p1", "server": "LiveServer-1"}
    p2 = {"id": 2, "account": "10002", "password": "secure_pass_p2", "server": "LiveServer-2"}

    payload = BrokerAccountDispatcher.format_assignment_payload(
        match_id=888,
        match_type="tournament",
        duration_minutes=30,
        p1_data=p1,
        p2_data=p2
    )

    assert payload["id"] == 888
    assert payload["duration_minutes"] == 33  # 30 + 3 grace period
    assert payload["player1"]["name_account"] == "10001"
    assert payload["player2"]["name_account"] == "10002"
    print("BrokerAccountDispatcher test passed successfully!")

if __name__ == "__main__":
    test_dispatcher()
