"""Enhanced event bus with persistence capabilities for microservice migration."""

from __future__ import annotations

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum


class EventStatus(Enum):
    """Status of an event in the system."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REPLAYED = "replayed"


@dataclass
class Event:
    """Enhanced event with metadata for persistence and replay."""
    id: str
    type: str
    payload: Dict[str, Any]
    timestamp: str
    version: int
    source: str
    correlation_id: Optional[str] = None
    status: EventStatus = EventStatus.PENDING
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @classmethod
    def create(cls, event_type: str, payload: Dict[str, Any], source: str = "unknown", 
               correlation_id: Optional[str] = None) -> "Event":
        """Create a new event with generated ID and timestamp."""
        return cls(
            id=str(uuid.uuid4()),
            type=event_type,
            payload=payload or {},
            timestamp=datetime.now().isoformat(),
            version=1,
            source=source,
            correlation_id=correlation_id,
            status=EventStatus.PENDING
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create event from dictionary."""
        if 'status' in data:
            data['status'] = EventStatus(data['status'])
        return cls(**data)


class EventStore(ABC):
    """Abstract interface for event storage."""
    
    @abstractmethod
    def store(self, event: Event) -> None:
        """Store an event."""
        pass
    
    @abstractmethod
    def get(self, event_id: str) -> Optional[Event]:
        """Get an event by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Event]:
        """Get all events."""
        pass
    
    @abstractmethod
    def get_by_type(self, event_type: str) -> List[Event]:
        """Get events by type."""
        pass
    
    @abstractmethod
    def get_by_source(self, source: str) -> List[Event]:
        """Get events by source."""
        pass
    
    @abstractmethod
    def get_by_correlation_id(self, correlation_id: str) -> List[Event]:
        """Get events by correlation ID."""
        pass
    
    @abstractmethod
    def get_since(self, timestamp: str) -> List[Event]:
        """Get events since a timestamp."""
        pass
    
    @abstractmethod
    def update_status(self, event_id: str, status: EventStatus) -> None:
        """Update event status."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all events."""
        pass


class FileEventStore(EventStore):
    """File-based event store using JSON."""
    
    def __init__(self, file_path: Union[str, Path] = ".events.json"):
        self.file_path = Path(file_path)
        self._events: Dict[str, Event] = {}
        self._load_events()
    
    def _load_events(self) -> None:
        """Load events from file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    self._events = {
                        event_id: Event.from_dict(event_data) 
                        for event_id, event_data in data.items()
                    }
            except (json.JSONDecodeError, KeyError):
                # If file is corrupted, start fresh
                self._events = {}
    
    def _save_events(self) -> None:
        """Save events to file."""
        try:
            with open(self.file_path, 'w') as f:
                data = {
                    event_id: event.to_dict() 
                    for event_id, event in self._events.items()
                }
                json.dump(data, f, indent=2)
        except Exception:
            # Fail silently to not break the application
            pass
    
    def store(self, event: Event) -> None:
        """Store an event."""
        self._events[event.id] = event
        self._save_events()
    
    def get(self, event_id: str) -> Optional[Event]:
        """Get an event by ID."""
        return self._events.get(event_id)
    
    def get_all(self) -> List[Event]:
        """Get all events sorted by timestamp."""
        return sorted(self._events.values(), key=lambda e: e.timestamp)
    
    def get_by_type(self, event_type: str) -> List[Event]:
        """Get events by type."""
        return [e for e in self._events.values() if e.type == event_type]
    
    def get_by_source(self, source: str) -> List[Event]:
        """Get events by source."""
        return [e for e in self._events.values() if e.source == source]
    
    def get_by_correlation_id(self, correlation_id: str) -> List[Event]:
        """Get events by correlation ID."""
        return [e for e in self._events.values() if e.correlation_id == correlation_id]
    
    def get_since(self, timestamp: str) -> List[Event]:
        """Get events since a timestamp."""
        return [e for e in self._events.values() if e.timestamp >= timestamp]
    
    def update_status(self, event_id: str, status: EventStatus) -> None:
        """Update event status."""
        if event_id in self._events:
            self._events[event_id].status = status
            self._save_events()
    
    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()
        if self.file_path.exists():
            self.file_path.unlink()


class InMemoryEventStore(EventStore):
    """In-memory event store for testing."""
    
    def __init__(self):
        self._events: Dict[str, Event] = {}
    
    def store(self, event: Event) -> None:
        """Store an event."""
        self._events[event.id] = event
    
    def get(self, event_id: str) -> Optional[Event]:
        """Get an event by ID."""
        return self._events.get(event_id)
    
    def get_all(self) -> List[Event]:
        """Get all events sorted by timestamp."""
        return sorted(self._events.values(), key=lambda e: e.timestamp)
    
    def get_by_type(self, event_type: str) -> List[Event]:
        """Get events by type."""
        return [e for e in self._events.values() if e.type == event_type]
    
    def get_by_source(self, source: str) -> List[Event]:
        """Get events by source."""
        return [e for e in self._events.values() if e.source == source]
    
    def get_by_correlation_id(self, correlation_id: str) -> List[Event]:
        """Get events by correlation ID."""
        return [e for e in self._events.values() if e.correlation_id == correlation_id]
    
    def get_since(self, timestamp: str) -> List[Event]:
        """Get events since a timestamp."""
        return [e for e in self._events.values() if e.timestamp >= timestamp]
    
    def update_status(self, event_id: str, status: EventStatus) -> None:
        """Update event status."""
        if event_id in self._events:
            self._events[event_id].status = status
    
    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()


class EventFilter:
    """Filter for querying events."""
    
    def __init__(self):
        self.event_type: Optional[str] = None
        self.source: Optional[str] = None
        self.correlation_id: Optional[str] = None
        self.status: Optional[EventStatus] = None
        self.since: Optional[str] = None
        self.until: Optional[str] = None
    
    def matches(self, event: Event) -> bool:
        """Check if event matches filter criteria."""
        if self.event_type and event.type != self.event_type:
            return False
        
        if self.source and event.source != self.source:
            return False
        
        if self.correlation_id and event.correlation_id != self.correlation_id:
            return False
        
        if self.status and event.status != self.status:
            return False
        
        if self.since and event.timestamp < self.since:
            return False
        
        if self.until and event.timestamp > self.until:
            return False
        
        return True


class EventReplayer:
    """Replays events for testing and debugging."""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
    
    def replay_all(self, handler: Callable[[Event], None]) -> List[Event]:
        """Replay all events."""
        events = self.event_store.get_all()
        replayed = []
        
        for event in events:
            try:
                handler(event)
                # Mark as replayed
                event.status = EventStatus.REPLAYED
                self.event_store.update_status(event.id, EventStatus.REPLAYED)
                replayed.append(event)
            except Exception as e:
                # Mark as failed
                event.metadata['replay_error'] = str(e)
                self.event_store.update_status(event.id, EventStatus.FAILED)
        
        return replayed
    
    def replay_by_type(self, event_type: str, handler: Callable[[Event], None]) -> List[Event]:
        """Replay events of specific type."""
        events = self.event_store.get_by_type(event_type)
        replayed = []
        
        for event in events:
            try:
                handler(event)
                event.status = EventStatus.REPLAYED
                self.event_store.update_status(event.id, EventStatus.REPLAYED)
                replayed.append(event)
            except Exception as e:
                event.metadata['replay_error'] = str(e)
                self.event_store.update_status(event.id, EventStatus.FAILED)
        
        return replayed
    
    def replay_correlation(self, correlation_id: str, handler: Callable[[Event], None]) -> List[Event]:
        """Replay events with same correlation ID."""
        events = self.event_store.get_by_correlation_id(correlation_id)
        replayed = []
        
        for event in sorted(events, key=lambda e: e.timestamp):
            try:
                handler(event)
                event.status = EventStatus.REPLAYED
                self.event_store.update_status(event.id, EventStatus.REPLAYED)
                replayed.append(event)
            except Exception as e:
                event.metadata['replay_error'] = str(e)
                self.event_store.update_status(event.id, EventStatus.FAILED)
        
        return replayed


class EventBus:
    """Enhanced event bus with persistence capabilities."""
    
    def __init__(self, event_store: Optional[EventStore] = None):
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_store = event_store or InMemoryEventStore()
        self._replayer = EventReplayer(self._event_store)
    
    def register(self, event_type: str, handler: Callable) -> None:
        """Register a handler for an event type."""
        self._handlers.setdefault(event_type, []).append(handler)
    
    def emit(self, event_type: str, payload: Dict[str, Any] = None, 
             source: str = "unknown", correlation_id: Optional[str] = None) -> Event:
        """Emit an event with persistence."""
        # Create event
        event = Event.create(event_type, payload or {}, source, correlation_id)
        
        # Store event
        self._event_store.store(event)
        
        # Update status to processing
        event.status = EventStatus.PROCESSING
        self._event_store.update_status(event.id, EventStatus.PROCESSING)
        
        # Call handlers
        success = True
        for handler in self._handlers.get(event_type, []):
            try:
                handler(payload or {})
            except Exception as e:
                success = False
                event.metadata['error'] = str(e)
        
        # Update final status
        final_status = EventStatus.COMPLETED if success else EventStatus.FAILED
        event.status = final_status
        self._event_store.update_status(event.id, final_status)
        
        return event
    
    def emit_legacy(self, event_type: str, payload=None) -> None:
        """Legacy emit method for backward compatibility."""
        self.emit(event_type, payload or {})
    
    def get_event_store(self) -> EventStore:
        """Get the event store."""
        return self._event_store
    
    def get_replayer(self) -> EventReplayer:
        """Get the event replayer."""
        return self._replayer
    
    def query_events(self, event_filter: EventFilter) -> List[Event]:
        """Query events using filter."""
        all_events = self._event_store.get_all()
        return [event for event in all_events if event_filter.matches(event)]
    
    def get_events_by_type(self, event_type: str) -> List[Event]:
        """Get events by type."""
        return self._event_store.get_by_type(event_type)
    
    def get_events_by_source(self, source: str) -> List[Event]:
        """Get events by source."""
        return self._event_store.get_by_source(source)
    
    def get_events_since(self, timestamp: str) -> List[Event]:
        """Get events since timestamp."""
        return self._event_store.get_since(timestamp)
    
    def get_event_history(self) -> List[Event]:
        """Get complete event history."""
        return self._event_store.get_all()
    
    def clear_events(self) -> None:
        """Clear all events."""
        self._event_store.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event statistics."""
        events = self._event_store.get_all()
        
        stats = {
            "total_events": len(events),
            "by_type": {},
            "by_status": {},
            "by_source": {},
            "recent_events": len([e for e in events if e.timestamp >= (datetime.now().isoformat()[:10])])
        }
        
        for event in events:
            # Count by type
            stats["by_type"][event.type] = stats["by_type"].get(event.type, 0) + 1
            
            # Count by status
            status_key = event.status.value
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1
            
            # Count by source
            stats["by_source"][event.source] = stats["by_source"].get(event.source, 0) + 1
        
        return stats