import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

from crucible.event_bus import EventBus


def test_event_bus():
    bus = EventBus()
    result = []

    def handler(payload):
        result.append(payload)

    bus.register('test', handler)
    bus.emit('test', 123)
    assert result == [123]
