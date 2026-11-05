---
trigger: always_on
---

# Incienso Shop: Models & ORM Guidelines

## Core Principles

1. **Inherit Standard Base Models (Single-Tenant)**:
   - Domain models (`Creator`, `Channel`, `StreamingSession`, `Video`, `VideoPublication`, `VideoRelation`, `ChannelAlert`, `ImportBatch`) MUST inherit from `BaseModel` (providing `created_at` and `updated_at`).
   - Do NOT include `tenant_id` or `organization_id` fields; the system is single-tenant for a single company.
2. **Audit History & Tagging**:
   - Include `history = HistoricalRecords()` (`django-simple-history`) on core mutable models (`Creator`, `Channel`, `Video`, `VideoPublication`, `ChannelAlert`).
   - Use `tags = TaggableManager(blank=True)` (`django-taggit`) instead of PostgreSQL-specific `ArrayField`.
3. **Database Constraints over Python Assertions (SQLite 3.31+ Compatible)**:
   - Enforce multi-column uniqueness via `models.UniqueConstraint`:
     ```python
     models.UniqueConstraint(
         fields=["creator", "platform", "platform_channel_id"],
         name="unique_creator_platform_channel",
     )
     ```
   - Use `models.CheckConstraint` for non-negative metrics (`views_count >= 0`, `duration_seconds >= 0`, `avg_ccv >= 0`) and relational integrity (e.g., `VideoRelation` must reference either `target_video` or `target_session`).
4. **Monetary & Calculated Fields**:
   - All financial amounts (`ad_revenue`, `subs_revenue`, `donations_revenue`, `total_earnings`, `production_cost`, `estimated_revenue`) MUST use `DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))`. Never use `FloatField`.
   - Use `models.GeneratedField` for deterministic SQL-level computed columns such as `hours_streamed` (`duration_seconds / 3600.0`).
5. **No Business Mutations in Models**:
   - Do NOT override `save()` to perform external calls, send emails, invalidate cache, or mutate related models.
   - Do NOT implement complex business workflows inside model methods; keep them in `services.py`.
