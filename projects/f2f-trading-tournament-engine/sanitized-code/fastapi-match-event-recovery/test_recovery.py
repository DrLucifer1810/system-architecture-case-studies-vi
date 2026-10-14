import asyncio
import json
from event_recovery import EventRecovery

class MockRedis:
    def __init__(self):
        self.streams = {}

    async def xadd(self, key, fields, maxlen=None, approximate=True):
        if key not in self.streams:
            self.streams[key] = []
        event_id = f"{len(self.streams[key]) + 1}-0"
        self.streams[key].append((event_id, fields))
        if maxlen and len(self.streams[key]) > maxlen:
            self.streams[key] = self.streams[key][-maxlen:]
        return event_id

    async def expire(self, key, ttl):
        return True

    async def xrevrange(self, key, count=10):
        if key not in self.streams:
            return []
        items = list(reversed(self.streams[key]))
        return items[:count]

async def test_recovery_flow():
    mock_redis = MockRedis()
    recovery = EventRecovery(mock_redis)

    # 1. Filtered event should be skipped
    skipped = await recovery.save_match_event(101, {'type': 'CHAT_MESSAGE', 'msg': 'hello'})
    assert not skipped

    # 2. Critical events should be recorded
    ok1 = await recovery.save_match_event(101, {'type': 'ORDER_OPENED', 'symbol': 'EURUSD', 'lots': 1.0})
    ok2 = await recovery.save_match_event(101, {'type': 'ORDER_CLOSED', 'profit': 150.0})
    assert ok1 and ok2

    # 3. Retrieve missed events on reconnect
    missed = await recovery.get_missed_events(101, count=10)
    assert len(missed) == 2
    assert missed[0]['type'] == 'ORDER_OPENED'
    assert missed[1]['type'] == 'ORDER_CLOSED'
    print("EventRecovery test passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_recovery_flow())
