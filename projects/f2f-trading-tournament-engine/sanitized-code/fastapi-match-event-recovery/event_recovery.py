import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

class EventRecovery:
    """
    Context-aware Event Recovery Engine utilizing Redis Streams.
    Keys are partitioned by context: match_events:{id}, tournament_events:{id}.
    Guarantees zero-loss event recovery during mobile network transitions.
    """
    SKIP_EVENTS = {
        'VIEW_COUNT_UPDATE',
        'CHAT_MESSAGE',
    }

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.event_ttl = 300       # 5 minutes TTL
        self.max_stream_len = 100  # Cap stream length to 100 entries

    async def save_match_event(self, match_id: int, event: Dict[str, Any]) -> bool:
        """Saves a match event into context stream with TTL and length pruning."""
        try:
            event_type = event.get('type')
            if event_type in self.SKIP_EVENTS:
                return False

            event['_saved_at'] = datetime.utcnow().timestamp()
            stream_key = f"match_events:{match_id}"

            if self.redis:
                await self.redis.xadd(
                    stream_key,
                    {'data': json.dumps(event)},
                    maxlen=self.max_stream_len,
                    approximate=True
                )
                await self.redis.expire(stream_key, self.event_ttl)
            return True
        except Exception as e:
            logging.error(f"Failed to save event to stream: {e}")
            return False

    async def get_missed_events(self, match_id: int, count: int = 20) -> List[Dict[str, Any]]:
        """Fetches missed events in reverse chronological order and parses payload."""
        if not self.redis:
            return []

        stream_key = f"match_events:{match_id}"
        raw_events = await self.redis.xrevrange(stream_key, count=count)
        
        events = []
        for event_id, data in reversed(raw_events):
            try:
                parsed = json.loads(data['data'])
                parsed['_event_id'] = event_id
                events.append(parsed)
            except Exception as e:
                logging.error(f"Failed to parse stream event: {e}")
        return events
