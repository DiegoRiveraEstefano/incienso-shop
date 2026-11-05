---
trigger: always_on
---

# Incienso Shop: Service Layer Guidelines

## Core Principles

1. **Stateless Service Classes**:
   - Services are defined as classes containing `@classmethod` methods.
   - Do NOT instantiate service objects (`Service()` is forbidden).
2. **Single-Company Domain Context**:
   - No `tenant_id` parameter is required. Pass explicit domain identifiers (`creator_id`, `channel_id`, `video_id`, `actor_user_id`) and typed primitives (`str`, `int`, `Decimal`, `datetime`).
3. **Decoupled from HTTP & UI**:
   - Services must NEVER accept `request`, `HttpRequest`, `Form`, or `WizardView` instances. Multi-step wizards must unpack their cleaned data payloads before invoking the service.
4. **Explicit Atomicity & SQLite Write Efficiency**:
   - Any service method modifying the database must be decorated with `@transaction.atomic`.
   - Keep transactions short to prevent SQLite write contention.
   - Invalidate relevant `DiskCache` analytical keys via `transaction.on_commit(...)`.
5. **Fail-Fast with Guard Clauses**:
   - Check preconditions at the beginning and raise `BusinessLogicError` (or domain-specific subclasses).
6. **Structured Logging**:
   - Emit event logs using standard `logging` with structured `extra={"creator_id": ...}`.

## Canonical Service Signature

```python
import logging
from decimal import Decimal
from django.db import transaction
from incienso_shop.analytics.services import AnalyticsCacheService
from incienso_shop.core.exceptions import BusinessLogicError
from .models import StreamingSession

logger = logging.getLogger(__name__)


class StreamingSessionService:
    @classmethod
    @transaction.atomic
    def record_session(
        cls,
        *,
        creator_id: int,
        channel_id: int | None,
        session_title: str,
        game_or_category: str,
        platform: str,
        streamed_at,
        duration_seconds: int,
        peak_viewers: int = 0,
        avg_ccv: int = 0,
        ad_revenue: Decimal = Decimal("0.00"),
        subs_revenue: Decimal = Decimal("0.00"),
        donations_revenue: Decimal = Decimal("0.00"),
    ) -> StreamingSession:
        log_ctx = {"creator_id": creator_id, "platform": platform}
        logger.info("streaming_session_record_started", extra=log_ctx)

        # 1. Guard clauses
        if duration_seconds < 0:
            raise BusinessLogicError("La duración de la sesión no puede ser negativa.")

        total_earnings = ad_revenue + subs_revenue + donations_revenue
        hours = Decimal(duration_seconds) / Decimal(3600) if duration_seconds > 0 else Decimal(0)
        earnings_per_hour = (total_earnings / hours).quantize(Decimal("0.01")) if hours > 0 else Decimal("0.00")

        # 2. Database mutation
        session = StreamingSession.objects.create(
            creator_id=creator_id,
            channel_id=channel_id,
            session_title=session_title,
            game_or_category=game_or_category,
            platform=platform,
            streamed_at=streamed_at,
            duration_seconds=duration_seconds,
            peak_viewers=peak_viewers,
            avg_ccv=avg_ccv,
            ad_revenue=ad_revenue,
            subs_revenue=subs_revenue,
            donations_revenue=donations_revenue,
            total_earnings=total_earnings,
            earnings_per_hour=earnings_per_hour,
        )

        # 3. Invalidate DiskCache analytics only after successful SQLite commit
        transaction.on_commit(AnalyticsCacheService.invalidate_all)

        logger.info("streaming_session_recorded", extra={**log_ctx, "session_id": session.id})
        return session
```
