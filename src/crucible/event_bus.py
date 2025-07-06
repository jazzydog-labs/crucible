class EventBus:
    """Simple in-process pub/sub bus."""

    def __init__(self):
        self._handlers = {}

    def register(self, event_type: str, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(self, event_type: str, payload=None):
        for handler in self._handlers.get(event_type, []):
            handler(payload)
