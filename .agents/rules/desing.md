---
trigger: always_on
---

# Incienso Shop: UI/UX & Bootstrap 5 Design System

## Styling Architecture

1. **Bootstrap 5 First**:
   - Use Bootstrap 5 layout (`container-fluid`, `row`, `col-*`), utilities (`d-flex`, `gap-*`, `p-*`, `m-*`), and components (`.card`, `.table`, `.badge`, `.btn`, `.alert`, `.offcanvas-lg`, `.modal`).
   - Support light and dark color modes via `data-bs-theme="light"` and `data-bs-theme="dark"`.
2. **Custom Domain Tokens (`project.css`)**:
   - Define platform brand tokens and metric typography in `:root` inside `incienso_shop/static/css/project.css`:
     - **Twitch**: `--platform-twitch-bg`, `--platform-twitch-text` (`#772ce8`)
     - **YouTube**: `--platform-youtube-bg`, `--platform-youtube-text` (`#cc0000`)
     - **Kick**: `--platform-kick-bg`, `--platform-kick-text` (`#1b7a00`)
     - **TikTok**: `--platform-tiktok-bg`, `--platform-tiktok-text` (`#007a76`)
     - **Metrics Font**: `--font-mono-metrics` with `font-variant-numeric: tabular-nums`

## Rules for UI & Forms

1. **Forms (`django-crispy-forms` & `django-widget-tweaks`)**:
   - Use `crispy-bootstrap5` (`FormHelper`, `Layout`, `Row`, `Column`, `Fieldset`) for all create/update forms.
   - Use `django-widget-tweaks` (`{% render_field %}`) for compact filter bars (`form-control-sm`, `form-select-sm`) in templates.
   - Never inject arbitrary inline `style="..."` attributes on form inputs.
2. **Data Tables (`django-tables2`)**:
   - Wrap tables in `.table-responsive` inside `.card.shadow-sm`.
   - Right-align all numeric and financial columns (`text-end tabular-nums`) so numbers align vertically (`avg_ccv`, `peak_viewers`, `views_count`, `hours_streamed`, `total_earnings`, `roi_percentage`, `rpm_estimated`).
3. **Semantic Status & Alert Badges**:
   - Creator Status: `active` (`.text-bg-success`), `inactive` (`.text-bg-secondary`), `suspended` (`.text-bg-danger`).
   - Channel Alert Severity: `info` (`.text-bg-info`), `warning` (`.text-bg-warning`), `critical` (`.text-bg-danger`).
