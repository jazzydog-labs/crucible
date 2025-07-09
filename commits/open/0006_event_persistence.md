# Persist Events for Later Microservice Extraction

## Status: OPEN

## Description
Implement event persistence to support the future evolution from monolith to microservices architecture.

## Requirements
- Add event storage mechanism to the EventBus
- Implement event replay capabilities
- Create event serialization/deserialization
- Add event versioning for backward compatibility
- Implement event querying and filtering
- Consider using event sourcing patterns

## Proposed Implementation
1. Create an event store interface
2. Implement file-based event storage (JSON/YAML)
3. Add event metadata (timestamp, version, source)
4. Create event replay mechanism for testing
5. Add event migration utilities for schema changes
6. Consider integration with message queues for future microservices

## Files to Change
- `src/crucible/event_bus.py`
- New event store implementation
- New event serialization modules

## Architecture Considerations
- This enables future decomposition into microservices
- Each service could replay events to rebuild state
- Supports debugging and auditing