import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

from crucible.event_bus import (
    Event, EventStatus, EventBus, EventStore, FileEventStore, InMemoryEventStore,
    EventFilter, EventReplayer
)


class TestEvent:
    def test_event_creation(self):
        event = Event.create("test_event", {"key": "value"}, "test_source")
        
        assert event.type == "test_event"
        assert event.payload == {"key": "value"}
        assert event.source == "test_source"
        assert event.version == 1
        assert event.status == EventStatus.PENDING
        assert event.id is not None
        assert event.timestamp is not None
        assert event.metadata == {}
    
    def test_event_with_correlation_id(self):
        correlation_id = "test-correlation-123"
        event = Event.create("test_event", {"data": "test"}, "source", correlation_id)
        
        assert event.correlation_id == correlation_id
    
    def test_event_serialization(self):
        event = Event.create("test_event", {"key": "value"}, "test_source")
        
        # Test to_dict
        event_dict = event.to_dict()
        assert event_dict["type"] == "test_event"
        assert event_dict["payload"] == {"key": "value"}
        assert event_dict["status"] == "pending"
        
        # Test from_dict
        restored_event = Event.from_dict(event_dict)
        assert restored_event.type == event.type
        assert restored_event.payload == event.payload
        assert restored_event.status == event.status
        assert restored_event.id == event.id
    
    def test_event_metadata_initialization(self):
        event = Event(
            id="test-id",
            type="test",
            payload={},
            timestamp="2023-01-01T00:00:00",
            version=1,
            source="test",
            metadata=None
        )
        
        assert event.metadata == {}


class TestInMemoryEventStore:
    def setup_method(self):
        self.store = InMemoryEventStore()
        self.event = Event.create("test_event", {"key": "value"}, "test_source")
    
    def test_store_and_get(self):
        self.store.store(self.event)
        
        retrieved = self.store.get(self.event.id)
        assert retrieved is not None
        assert retrieved.id == self.event.id
        assert retrieved.type == self.event.type
    
    def test_get_nonexistent(self):
        result = self.store.get("nonexistent-id")
        assert result is None
    
    def test_get_all(self):
        event1 = Event.create("event1", {}, "source1")
        event2 = Event.create("event2", {}, "source2")
        
        self.store.store(event1)
        self.store.store(event2)
        
        all_events = self.store.get_all()
        assert len(all_events) == 2
        assert all_events[0].id in [event1.id, event2.id]
        assert all_events[1].id in [event1.id, event2.id]
    
    def test_get_by_type(self):
        event1 = Event.create("type1", {}, "source")
        event2 = Event.create("type2", {}, "source")
        event3 = Event.create("type1", {}, "source")
        
        self.store.store(event1)
        self.store.store(event2)
        self.store.store(event3)
        
        type1_events = self.store.get_by_type("type1")
        assert len(type1_events) == 2
        assert all(e.type == "type1" for e in type1_events)
    
    def test_get_by_source(self):
        event1 = Event.create("event", {}, "source1")
        event2 = Event.create("event", {}, "source2")
        event3 = Event.create("event", {}, "source1")
        
        self.store.store(event1)
        self.store.store(event2)
        self.store.store(event3)
        
        source1_events = self.store.get_by_source("source1")
        assert len(source1_events) == 2
        assert all(e.source == "source1" for e in source1_events)
    
    def test_get_by_correlation_id(self):
        corr_id = "test-correlation"
        event1 = Event.create("event", {}, "source", corr_id)
        event2 = Event.create("event", {}, "source", "other-correlation")
        event3 = Event.create("event", {}, "source", corr_id)
        
        self.store.store(event1)
        self.store.store(event2)
        self.store.store(event3)
        
        corr_events = self.store.get_by_correlation_id(corr_id)
        assert len(corr_events) == 2
        assert all(e.correlation_id == corr_id for e in corr_events)
    
    def test_get_since(self):
        # Create events with different timestamps
        with patch('crucible.event_bus.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T10:00:00"
            event1 = Event.create("event", {}, "source")
            
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
            event2 = Event.create("event", {}, "source")
        
        self.store.store(event1)
        self.store.store(event2)
        
        since_events = self.store.get_since("2023-01-01T11:00:00")
        assert len(since_events) == 1
        assert since_events[0].id == event2.id
    
    def test_update_status(self):
        self.store.store(self.event)
        
        self.store.update_status(self.event.id, EventStatus.COMPLETED)
        
        retrieved = self.store.get(self.event.id)
        assert retrieved.status == EventStatus.COMPLETED
    
    def test_clear(self):
        self.store.store(self.event)
        assert len(self.store.get_all()) == 1
        
        self.store.clear()
        assert len(self.store.get_all()) == 0


class TestFileEventStore:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.store = FileEventStore(self.temp_file.name)
        self.event = Event.create("test_event", {"key": "value"}, "test_source")
    
    def teardown_method(self):
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_store_and_load(self):
        self.store.store(self.event)
        
        # Create new store with same file
        new_store = FileEventStore(self.temp_file.name)
        retrieved = new_store.get(self.event.id)
        
        assert retrieved is not None
        assert retrieved.id == self.event.id
        assert retrieved.type == self.event.type
        assert retrieved.payload == self.event.payload
    
    def test_persistent_storage(self):
        event1 = Event.create("event1", {"data": "test1"}, "source1")
        event2 = Event.create("event2", {"data": "test2"}, "source2")
        
        self.store.store(event1)
        self.store.store(event2)
        
        # Verify file contents
        with open(self.temp_file.name, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert event1.id in data
        assert event2.id in data
        assert data[event1.id]["type"] == "event1"
        assert data[event2.id]["type"] == "event2"
    
    def test_corrupted_file_handling(self):
        # Write corrupted JSON
        with open(self.temp_file.name, 'w') as f:
            f.write("invalid json content")
        
        # Should handle corruption gracefully
        store = FileEventStore(self.temp_file.name)
        assert len(store.get_all()) == 0
    
    def test_clear_removes_file(self):
        self.store.store(self.event)
        assert Path(self.temp_file.name).exists()
        
        self.store.clear()
        assert not Path(self.temp_file.name).exists()


class TestEventFilter:
    def setup_method(self):
        self.filter = EventFilter()
        self.event = Event.create("test_event", {"key": "value"}, "test_source")
    
    def test_empty_filter_matches_all(self):
        assert self.filter.matches(self.event) is True
    
    def test_type_filter(self):
        self.filter.event_type = "test_event"
        assert self.filter.matches(self.event) is True
        
        self.filter.event_type = "other_event"
        assert self.filter.matches(self.event) is False
    
    def test_source_filter(self):
        self.filter.source = "test_source"
        assert self.filter.matches(self.event) is True
        
        self.filter.source = "other_source"
        assert self.filter.matches(self.event) is False
    
    def test_status_filter(self):
        self.filter.status = EventStatus.PENDING
        assert self.filter.matches(self.event) is True
        
        self.filter.status = EventStatus.COMPLETED
        assert self.filter.matches(self.event) is False
    
    def test_timestamp_filter(self):
        # Test since filter
        self.filter.since = "2020-01-01T00:00:00"
        assert self.filter.matches(self.event) is True
        
        self.filter.since = "2030-01-01T00:00:00"
        assert self.filter.matches(self.event) is False
        
        # Test until filter
        self.filter.since = None
        self.filter.until = "2030-01-01T00:00:00"
        assert self.filter.matches(self.event) is True
        
        self.filter.until = "2020-01-01T00:00:00"
        assert self.filter.matches(self.event) is False


class TestEventReplayer:
    def setup_method(self):
        self.store = InMemoryEventStore()
        self.replayer = EventReplayer(self.store)
        self.handler = Mock()
        
        # Create test events
        self.event1 = Event.create("event1", {"data": "test1"}, "source1")
        self.event2 = Event.create("event2", {"data": "test2"}, "source2")
        self.event3 = Event.create("event1", {"data": "test3"}, "source1")
        
        self.store.store(self.event1)
        self.store.store(self.event2)
        self.store.store(self.event3)
    
    def test_replay_all(self):
        replayed = self.replayer.replay_all(self.handler)
        
        assert len(replayed) == 3
        assert self.handler.call_count == 3
        
        # Check all events were marked as replayed
        for event in replayed:
            assert event.status == EventStatus.REPLAYED
    
    def test_replay_by_type(self):
        replayed = self.replayer.replay_by_type("event1", self.handler)
        
        assert len(replayed) == 2
        assert self.handler.call_count == 2
        
        # Check only event1 type events were replayed
        for event in replayed:
            assert event.type == "event1"
            assert event.status == EventStatus.REPLAYED
    
    def test_replay_with_correlation_id(self):
        # Add events with correlation IDs
        corr_id = "test-correlation"
        event_with_corr1 = Event.create("event", {"data": "corr1"}, "source", corr_id)
        event_with_corr2 = Event.create("event", {"data": "corr2"}, "source", corr_id)
        
        self.store.store(event_with_corr1)
        self.store.store(event_with_corr2)
        
        replayed = self.replayer.replay_correlation(corr_id, self.handler)
        
        assert len(replayed) == 2
        assert self.handler.call_count == 2
        
        for event in replayed:
            assert event.correlation_id == corr_id
            assert event.status == EventStatus.REPLAYED
    
    def test_replay_with_handler_error(self):
        def failing_handler(event):
            if event.type == "event2":
                raise ValueError("Test error")
        
        replayed = self.replayer.replay_all(failing_handler)
        
        # Should still replay all events
        assert len(replayed) == 2  # Two successful replays
        
        # Check that failed event is marked as failed
        failed_event = self.store.get(self.event2.id)
        assert failed_event.status == EventStatus.FAILED
        assert 'replay_error' in failed_event.metadata


class TestEventBus:
    def setup_method(self):
        self.store = InMemoryEventStore()
        self.bus = EventBus(self.store)
        self.handler = Mock()
    
    def test_register_and_emit(self):
        self.bus.register("test_event", self.handler)
        
        event = self.bus.emit("test_event", {"data": "test"}, "test_source")
        
        assert event.type == "test_event"
        assert event.payload == {"data": "test"}
        assert event.source == "test_source"
        assert event.status == EventStatus.COMPLETED
        
        self.handler.assert_called_once_with({"data": "test"})
    
    def test_emit_with_correlation_id(self):
        correlation_id = "test-correlation"
        event = self.bus.emit("test_event", {"data": "test"}, "source", correlation_id)
        
        assert event.correlation_id == correlation_id
    
    def test_emit_with_handler_error(self):
        def failing_handler(payload):
            raise ValueError("Handler error")
        
        self.bus.register("test_event", failing_handler)
        
        event = self.bus.emit("test_event", {"data": "test"}, "source")
        
        assert event.status == EventStatus.FAILED
        assert 'error' in event.metadata
    
    def test_emit_legacy_backward_compatibility(self):
        self.bus.register("test_event", self.handler)
        
        # Test legacy emit method
        self.bus.emit_legacy("test_event", {"data": "test"})
        
        self.handler.assert_called_once_with({"data": "test"})
        
        # Check event was stored
        events = self.bus.get_event_history()
        assert len(events) == 1
        assert events[0].type == "test_event"
    
    def test_query_events(self):
        # Create multiple events
        self.bus.emit("event1", {"data": "test1"}, "source1")
        self.bus.emit("event2", {"data": "test2"}, "source2")
        self.bus.emit("event1", {"data": "test3"}, "source1")
        
        # Query by type
        filter_by_type = EventFilter()
        filter_by_type.event_type = "event1"
        
        events = self.bus.query_events(filter_by_type)
        assert len(events) == 2
        assert all(e.type == "event1" for e in events)
    
    def test_get_events_by_type(self):
        self.bus.emit("event1", {"data": "test1"}, "source")
        self.bus.emit("event2", {"data": "test2"}, "source")
        self.bus.emit("event1", {"data": "test3"}, "source")
        
        events = self.bus.get_events_by_type("event1")
        assert len(events) == 2
        assert all(e.type == "event1" for e in events)
    
    def test_get_events_by_source(self):
        self.bus.emit("event", {"data": "test1"}, "source1")
        self.bus.emit("event", {"data": "test2"}, "source2")
        self.bus.emit("event", {"data": "test3"}, "source1")
        
        events = self.bus.get_events_by_source("source1")
        assert len(events) == 2
        assert all(e.source == "source1" for e in events)
    
    def test_get_event_history(self):
        self.bus.emit("event1", {"data": "test1"}, "source")
        self.bus.emit("event2", {"data": "test2"}, "source")
        
        history = self.bus.get_event_history()
        assert len(history) == 2
        assert history[0].type in ["event1", "event2"]
        assert history[1].type in ["event1", "event2"]
    
    def test_clear_events(self):
        self.bus.emit("event", {"data": "test"}, "source")
        assert len(self.bus.get_event_history()) == 1
        
        self.bus.clear_events()
        assert len(self.bus.get_event_history()) == 0
    
    def test_get_stats(self):
        self.bus.emit("event1", {"data": "test1"}, "source1")
        self.bus.emit("event2", {"data": "test2"}, "source2")
        self.bus.emit("event1", {"data": "test3"}, "source1")
        
        stats = self.bus.get_stats()
        
        assert stats["total_events"] == 3
        assert stats["by_type"]["event1"] == 2
        assert stats["by_type"]["event2"] == 1
        assert stats["by_source"]["source1"] == 2
        assert stats["by_source"]["source2"] == 1
        assert stats["by_status"]["completed"] == 3
    
    def test_get_event_store(self):
        store = self.bus.get_event_store()
        assert store is self.store
    
    def test_get_replayer(self):
        replayer = self.bus.get_replayer()
        assert isinstance(replayer, EventReplayer)
        assert replayer.event_store is self.store
    
    def test_legacy_compatibility(self):
        """Test that the original EventBus functionality still works."""
        bus = EventBus()
        result = []

        def handler(payload):
            result.append(payload)

        bus.register('test', handler)
        bus.emit_legacy('test', 123)
        assert result == [123]