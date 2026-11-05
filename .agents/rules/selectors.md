---
trigger: always_on
---

# RRSSRRSS CreatorsCreators AnalyzerAnalyzer: Selector Layer Guidelines

## Core Principles

1. **Read-Only Purity**:
   - Selectors contain ONLY query, aggregation, and data retrieval logic.
   - Zero database mutations, zero side-effects.
2. **Django Permission-Based Visibility Scoping**:
   - Never check hardcoded role columns on `User`. Use Django's native permission system (`user.has_perm(...)`) and groups.
   - When querying creator-owned entities (`Creator`, `Channel`, `StreamingSession`, `Video`, `VideoPublication`, `ChannelAlert`), accept `user: User` and scope appropriately:
     - Users with the global permission (e.g. `user.has_perm("streams.view_all_sessions")`) can access the entire company catalog.
     - Users without the global permission (e.g. members of the `Creator` group) only see records where `creator__user=user`.
3. **Elimination of N+1 Queries**:
   - Always specify `select_related("creator", "channel")` for foreign keys and one-to-one relationships.
   - Always specify `prefetch_related("tags", "publications")` for reverse foreign keys and many-to-many relationships.
4. **Django ORM Aggregations & DiskCache for Analytics**:
   - Replace legacy PostgreSQL materialized views (`mv_*`) and SQL views (`v_*`) with Django ORM queries (`annotate`, `aggregate`, `Window(expression=DenseRank())`, `TruncDay`, `TruncMonth`) cached in `DiskCache` (`cache.get_or_set(...)`).
   - Return `QuerySet`s for views using `django-filter` and `django-tables2` so filtering, sorting, and pagination can be chained cleanly.
   - Always specify `select_related("creator", "channel")` for foreign keys and one-to-one relationships.
   - Always specify `prefetch_related("tags", "publications")` for reverse foreign keys and many-to-many relationships.
4. **Django ORM Aggregations & DiskCache for Analytics**:
   - Replace legacy PostgreSQL materialized views (`mv_*`) with SQLite views / Django ORM queries (`annotate`, `aggregate`, `Window(expression=DenseRank())`, `TruncDay`, `TruncMonth`) cached in `DiskCache` (`cache.get_or_set(...)`).
   - Return `QuerySet`s for views using `django-filter` and `django-tables2` so filtering, sorting, and pagination can be chained cleanly.

## Canonical Selector Implementation

```python
from typing import Optional
from django.core.cache import cache
from django.db.models import QuerySet
from incienso_shopincienso_shop.apps.usersusers.modelsmodels import (
    User,
    UserRoleUser,
)
from .models import StreamingSessionStreamingSession


class StreamingSessionSelectorStreamingSessionSelector:
    @classmethod
    def get_visible_queryset(cls, *, user: User) -> QuerySet[StreamingSession]:
        qs = StreamingSession.objects.select_related("creator", "channel", "import_batch")
        if user.role == UserRole.CREATOR:
            return qs.filter(creator__user=user)
        return qs.order_by("-streamed_at")

    def get_visible_queryset(cls, *, user: User) -> QuerySet[StreamingSession]:
        qs = StreamingSession.objects.select_related("creator", "channel", "import_batch")
        if user.has_perm("streams.view_all_sessions"):
            return qs.order_by("-streamed_at")
        return qs.filter(creator__user=user).order_by("-streamed_at")

    @classmethod
    def get_by_id(cls, *, user: User, session_id: int) -> Optional[StreamingSession]:
        return cls.get_visible_queryset(user=user).filter(id=session_id).first()

    def get_by_id(cls, *, user: User, session_id: int) -> Optional[StreamingSession]:
        return cls.get_visible_queryset(user=user).filter(id=session_id).first()
```
