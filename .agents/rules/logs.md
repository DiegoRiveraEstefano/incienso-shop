---
trigger: always_on
---

# Incienso Shop: Logging Standards

## Core Rules

1. **Standard Python Logging Only**:
   - `import logging; logger = logging.getLogger(__name__)`.
   - `structlog` and custom logging wrappers are **STRICTLY PROHIBITED**.
2. **Static Event Strings**:
   - Use `snake_case` static identifiers as the message string (e.g., `logger.info("streaming_session_recorded", extra=...)`).
   - Never use f-strings or string interpolation in the message identifier.
3. **Structured Extra Metadata**:
   - Pass contextual business data in the `extra` dictionary:
     - Include domain entity IDs (`user_id`, `creator_id`, `channel_id`, `session_id`, `video_id`, `alert_id`, `batch_id`).
4. **Log Levels**:
   - `DEBUG`: Query parameters, `DiskCache` hits/misses, internal metric calculations.
   - `INFO`: Business operational milestones (`creator_created`, `streaming_session_recorded`, `video_published`, `alert_resolved`, `import_batch_completed`).
   - `WARNING`: Recoverable anomalies (`import_row_validation_failed`, `channel_alert_triggered`).
   - `ERROR`: Business exceptions, file parsing failures.
   - `EXCEPTION`: Inside `except` blocks only (auto-captures traceback).

## Prohibited vs. Correct

| Prohibited | Correct |
|---|---|
| `import structlog` | `import logging` |
| `logger.info(f"Creator {c.id} session recorded on {s.platform}")` | `logger.info("streaming_session_recorded", extra={"creator_id": c.id, "session_id": s.id, "platform": s.platform})` |
| `logger.error("Failed: " + str(e))` | `logger.exception("import_batch_failed", extra={"batch_id": batch.id})` |
