---
trigger: always_on
---

# Incienso Shop: Strict Signals Policy

## Forbidden Practices

> [!WARNING]
> The following usages of Django signals (`post_save`, `pre_save`, `m2m_changed`, `post_delete`) are **STRICTLY PROHIBITED**:
> - Triggering emails, notifications, or external API calls.
> - Enqueuing asynchronous background tasks.
> - Performing cascade mutations or metric recalculations on related domain models (`Creator`, `Video`, `StreamingSession`).
> - Mutating financial totals, ROI, or alert statuses.

## Permitted Usages

Django signals are ONLY permitted for low-level infrastructure hooks:
1. Setting SQLite performance pragmas (`journal_mode=WAL`, `synchronous=NORMAL`, `foreign_keys=ON`) on `connection_created`.
2. Internal audit trail hooks managed by `django-simple-history` (`HistoricalRecords`).

## Correct Replacement: Explicit Service Calls + `transaction.on_commit`

```python
# Prohibited (Signal anti-pattern)
@receiver(post_save, sender=StreamingSession)
def refresh_creator_cache(sender, instance, created, **kwargs):
    AnalyticsCacheService.invalidate_all()  # RISKY: runs even if transaction rolls back!

# Required (Explicit Service Call + transaction.on_commit)
class StreamingSessionService:
    @classmethod
    @transaction.atomic
    def record_session(cls, *, creator_id: int, ...) -> StreamingSession:
        session = StreamingSession.objects.create(creator_id=creator_id, ...)

        # Ensures DiskCache is only invalidated after SQLite commits cleanly
        transaction.on_commit(AnalyticsCacheService.invalidate_all)
        return session
```
