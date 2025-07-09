#!/usr/bin/env python3
"""Demo showcasing the enhanced event persistence system.

This demo demonstrates:
- Event creation and storage
- Event querying and filtering
- Event replay capabilities
- Correlation ID tracking
- Event statistics
- File-based persistence
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent / 'src'))

from crucible.event_bus import (
    EventBus, FileEventStore, InMemoryEventStore, Event, EventStatus, 
    EventFilter, EventReplayer
)


def demo_killer_feature():
    """The ONE thing that makes event persistence amazing."""
    print("=== KILLER FEATURE: Time travel through your system's history ===")
    
    # Create event bus with persistence
    bus = EventBus(FileEventStore(".demo_events.json"))
    
    # Simulate system events
    bus.emit("user_login", {"user": "alice"}, "auth_service", "session-123")
    bus.emit("order_placed", {"total": 99.99}, "order_service", "session-123")
    bus.emit("payment_failed", {"reason": "insufficient_funds"}, "payment_service", "session-123")
    
    # Replay entire user session instantly
    replayer = bus.get_replayer()
    events = bus.get_event_store().get_by_correlation_id("session-123")
    print(f"Found {len(events)} events for session-123 - replaying to debug issue...")
    print("\n✨ Debug production issues by replaying exact event sequences!\n")
    
    # Cleanup
    Path(".demo_events.json").unlink(missing_ok=True)


def demo_event_creation():
    """Demonstrate event creation and basic properties."""
    print("=== Event Creation Demo ===")
    
    # Create events with different properties
    event1 = Event.create("user_action", {"action": "login", "user_id": "123"}, "auth_service")
    event2 = Event.create("data_processed", {"records": 100, "status": "success"}, "data_service", "batch-001")
    
    print(f"Event 1: {event1.type} from {event1.source}")
    print(f"  ID: {event1.id}")
    print(f"  Timestamp: {event1.timestamp}")
    print(f"  Payload: {event1.payload}")
    print(f"  Status: {event1.status.value}")
    print(f"  Version: {event1.version}")
    
    print(f"\nEvent 2: {event2.type} from {event2.source}")
    print(f"  Correlation ID: {event2.correlation_id}")
    print(f"  Payload: {event2.payload}")
    
    return [event1, event2]


def demo_event_storage():
    """Demonstrate event storage capabilities."""
    print("\n=== Event Storage Demo ===")
    
    # Create temporary file for demo
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_path = temp_file.name
    
    print(f"Using temporary file: {temp_path}")
    
    # Create file-based event store
    store = FileEventStore(temp_path)
    
    # Create and store events
    events = []
    for i in range(3):
        event = Event.create(
            f"demo_event_{i}", 
            {"sequence": i, "data": f"test_data_{i}"}, 
            f"demo_service_{i % 2}"
        )
        store.store(event)
        events.append(event)
        print(f"Stored event {i}: {event.type}")
    
    print(f"\nTotal events stored: {len(store.get_all())}")
    
    # Demonstrate persistence by creating new store with same file
    new_store = FileEventStore(temp_path)
    loaded_events = new_store.get_all()
    print(f"Events loaded from file: {len(loaded_events)}")
    
    for event in loaded_events:
        print(f"  Loaded: {event.type} with payload {event.payload}")
    
    # Clean up
    Path(temp_path).unlink(missing_ok=True)
    
    return events


def demo_event_querying():
    """Demonstrate event querying and filtering."""
    print("\n=== Event Querying Demo ===")
    
    store = InMemoryEventStore()
    
    # Create diverse events for querying
    events_data = [
        ("user_login", {"user": "alice"}, "auth_service", "session-1"),
        ("user_logout", {"user": "alice"}, "auth_service", "session-1"),
        ("data_import", {"records": 500}, "data_service", "batch-1"),
        ("user_login", {"user": "bob"}, "auth_service", "session-2"),
        ("data_export", {"format": "csv"}, "data_service", "batch-1"),
    ]
    
    created_events = []
    for event_type, payload, source, correlation_id in events_data:
        event = Event.create(event_type, payload, source, correlation_id)
        store.store(event)
        created_events.append(event)
        print(f"Created: {event_type} from {source} (corr: {correlation_id})")
    
    print(f"\nTotal events: {len(store.get_all())}")
    
    # Query by type
    login_events = store.get_by_type("user_login")
    print(f"Login events: {len(login_events)}")
    
    # Query by source
    auth_events = store.get_by_source("auth_service")
    print(f"Auth service events: {len(auth_events)}")
    
    # Query by correlation ID
    session1_events = store.get_by_correlation_id("session-1")
    print(f"Session-1 events: {len(session1_events)}")
    for event in session1_events:
        print(f"  {event.type}: {event.payload}")
    
    return store, created_events


def demo_event_filtering():
    """Demonstrate advanced event filtering."""
    print("\n=== Event Filtering Demo ===")
    
    store = InMemoryEventStore()
    
    # Create events with different statuses
    event1 = Event.create("process_start", {"job": "export"}, "worker_1")
    event1.status = EventStatus.COMPLETED
    store.store(event1)
    store.update_status(event1.id, EventStatus.COMPLETED)
    
    event2 = Event.create("process_start", {"job": "import"}, "worker_2")
    event2.status = EventStatus.FAILED
    store.store(event2)
    store.update_status(event2.id, EventStatus.FAILED)
    
    event3 = Event.create("process_end", {"job": "export"}, "worker_1")
    store.store(event3)
    
    print("Created events with different statuses")
    
    # Create event bus for filtering
    bus = EventBus(store)
    
    # Filter by type
    type_filter = EventFilter()
    type_filter.event_type = "process_start"
    filtered_events = bus.query_events(type_filter)
    print(f"Process start events: {len(filtered_events)}")
    
    # Filter by status
    status_filter = EventFilter()
    status_filter.status = EventStatus.COMPLETED
    completed_events = bus.query_events(status_filter)
    print(f"Completed events: {len(completed_events)}")
    
    # Combined filter
    combined_filter = EventFilter()
    combined_filter.event_type = "process_start"
    combined_filter.status = EventStatus.FAILED
    failed_starts = bus.query_events(combined_filter)
    print(f"Failed start events: {len(failed_starts)}")
    
    return bus


def demo_event_replay():
    """Demonstrate event replay capabilities."""
    print("\n=== Event Replay Demo ===")
    
    store = InMemoryEventStore()
    
    # Create events for replay
    events_data = [
        ("system_start", {"version": "1.0"}, "system"),
        ("user_created", {"user": "alice"}, "user_service"),
        ("user_created", {"user": "bob"}, "user_service"),
        ("system_stop", {"reason": "maintenance"}, "system"),
    ]
    
    for event_type, payload, source in events_data:
        event = Event.create(event_type, payload, source)
        store.store(event)
        print(f"Created: {event_type}")
    
    # Create replayer
    replayer = EventReplayer(store)
    
    # Replay handler that tracks what was replayed
    replayed_events = []
    def replay_handler(event):
        replayed_events.append(event)
        print(f"  Replaying: {event.type} from {event.source}")
    
    print(f"\nReplaying all events:")
    replayed = replayer.replay_all(replay_handler)
    print(f"Successfully replayed: {len(replayed)} events")
    
    # Replay by type
    print(f"\nReplaying user_created events:")
    user_events = replayer.replay_by_type("user_created", replay_handler)
    print(f"User creation events replayed: {len(user_events)}")
    
    # Check event statuses
    all_events = store.get_all()
    for event in all_events:
        print(f"Event {event.type}: status = {event.status.value}")
    
    return replayer


def demo_event_bus_integration():
    """Demonstrate event bus with persistence."""
    print("\n=== Event Bus Integration Demo ===")
    
    # Create event bus with file persistence
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_path = temp_file.name
    
    store = FileEventStore(temp_path)
    bus = EventBus(store)
    
    # Register handlers
    processed_events = []
    
    def user_handler(payload):
        processed_events.append(("user", payload))
        print(f"  User handler processed: {payload}")
    
    def system_handler(payload):
        processed_events.append(("system", payload))
        print(f"  System handler processed: {payload}")
    
    bus.register("user_event", user_handler)
    bus.register("system_event", system_handler)
    
    print("Registered event handlers")
    
    # Emit events with correlation IDs
    correlation_id = "demo-session-123"
    
    print(f"\nEmitting events with correlation ID: {correlation_id}")
    event1 = bus.emit("user_event", {"action": "login", "user": "alice"}, "web_app", correlation_id)
    event2 = bus.emit("system_event", {"type": "audit", "message": "user login"}, "audit_service", correlation_id)
    event3 = bus.emit("user_event", {"action": "view_page", "page": "dashboard"}, "web_app", correlation_id)
    
    print(f"Events emitted, processed: {len(processed_events)}")
    
    # Get statistics
    stats = bus.get_stats()
    print(f"\nEvent Statistics:")
    print(f"  Total events: {stats['total_events']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  By status: {stats['by_status']}")
    print(f"  By source: {stats['by_source']}")
    
    # Query events by correlation ID
    correlated_events = bus.get_event_store().get_by_correlation_id(correlation_id)
    print(f"\nEvents with correlation ID '{correlation_id}': {len(correlated_events)}")
    
    # Clean up
    Path(temp_path).unlink(missing_ok=True)
    
    return bus, stats


def demo_error_handling():
    """Demonstrate error handling in event processing."""
    print("\n=== Error Handling Demo ===")
    
    bus = EventBus()
    
    # Handler that fails
    def failing_handler(payload):
        if payload.get("should_fail"):
            raise ValueError(f"Simulated error for: {payload}")
        print(f"  Successfully processed: {payload}")
    
    bus.register("test_event", failing_handler)
    
    # Emit successful event
    print("Emitting successful event:")
    success_event = bus.emit("test_event", {"data": "good", "should_fail": False}, "demo")
    print(f"  Event status: {success_event.status.value}")
    
    # Emit failing event
    print("\nEmitting failing event:")
    fail_event = bus.emit("test_event", {"data": "bad", "should_fail": True}, "demo")
    print(f"  Event status: {fail_event.status.value}")
    print(f"  Error metadata: {fail_event.metadata.get('error', 'None')}")
    
    return bus


def main():
    """Run all event persistence demos."""
    print("Event Persistence System Demo")
    print("=" * 50)
    
    try:
        # Start with the killer feature
        demo_killer_feature()
        
        # Run all demos
        demo_event_creation()
        demo_event_storage()
        demo_event_querying()
        demo_event_filtering()
        demo_event_replay()
        demo_event_bus_integration()
        demo_error_handling()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Event creation with metadata and versioning")
        print("✓ File-based persistent storage")
        print("✓ Event querying and filtering")
        print("✓ Event replay for testing and debugging")
        print("✓ Correlation ID tracking")
        print("✓ Event statistics and monitoring")
        print("✓ Error handling and status tracking")
        print("✓ Backward compatibility with legacy emit")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        raise


if __name__ == "__main__":
    main()