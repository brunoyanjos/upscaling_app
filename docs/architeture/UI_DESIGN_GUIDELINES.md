# Upscaling App — Desktop UI Design Guidelines

**Scope:** All desktop interfaces in `src/upscaling_app/gui/` (PySide6).

## Core principles

- Maintain a **4 px spacing grid**. Widget margins, layout spacing, internal padding, radii, and control heights should use multiples of 4.
- Use the tokens from `upscaling_app.gui.theme`; do not introduce new arbitrary values in individual views.
- Prioritize scientific legibility: consistent units, labels, sufficient contrast, visible validation feedback, and clear separation between user inputs and model outputs.
- Do not embed physical models, optimizers, or data ingestion inside Qt widgets. Views consume the scientific prediction API and persisted data.
- Keep ordinary UI text in English, matching the existing prototype. Explanatory help can be localized later.

## Spacing scale

| Token | Pixels | Purpose |
| --- | ---: | --- |
| `xs` | 4 | Icon/text gap and tight grouping |
| `sm` | 8 | Title-to-description gap, small widgets |
| `md` | 12 | Internal group spacing |
| `lg` | 16 | Common component padding and gaps |
| `xl` | 24 | Card padding, related sections |
| `xxl` | 32 | Main viewport padding and major section separation |
| `huge` | 48 | Large visual breathing space |
| `massive` | 64 | Only when a large desktop layout requires it |

## Desktop typography

| Token | Font size | Target line height | Primary use |
| --- | ---: | ---: | --- |
| `h1` | 32 px | 40 px | Screen title |
| `h2` | 28 px | 36 px | Section title and large result value |
| `h3` | 20 px | 28 px | Card title |
| `body_lg` | 18 px | 28 px | Emphasized prose |
| `body_md` | 16 px | 24 px | Standard text, controls |
| `body_sm` | 14 px | 20 px | Secondary text, notes |
| `caption` | 12 px | 16 px | Rare, nonessential microcopy |

**Qt limitation:** Qt Style Sheets do not implement web CSS `line-height`. Use the token's font size in QSS, and set appropriate minimum height or layout spacing where needed. For wrapped text, allow Qt's layout engine to determine the required height. Check the appearance on Windows, Linux/WSLg, and macOS with real system scaling; Qt logical pixels are not necessarily physical display pixels.

## Components and behavior

- Use Qt layout managers (not absolute coordinates) for content.
- Main content: 32 px margins; cards: 24 px padding; ordinary gaps: 8–24 px.
- All controls must show selected, hover, keyboard-focus, and disabled states when applicable.
- Prefer **in-window selection buttons** for short choices (2–4 options); avoid separate popup surfaces where platform/WSLg issues are known.
- Do not show a calculation result unless the scientific prediction has actually run.
- All numeric controls must display user-facing units explicitly. Convert input values to SI at the view/service boundary.
- Keep unsupported features visibly inactive rather than appearing to work.
- Do not hard-code calibration coefficients in a Qt component. Read persisted calibrations once and reuse the values.

## Project integration

Shared tokens and styles live in `src/upscaling_app/gui/theme.py`. Individual views such as `ssdi_window.py` use these shared tokens. Add a reference to this document in `AGENTS.md` so future coding agents follow the same conventions.

## SSDI prototype — interaction and maintainability checkpoint (2026-10-19)

- Continue using `theme.py` as the single source for colours, spacing, radii, and typography. Supported application text-size options are 100%, 125%, and 150% (in addition to OS DPI scaling).
- The four calibration choices must show selected and disabled states. Oil-wise is unavailable for `Custom oil` and has one calibrated `A,B` pair per eligible registered oil.
- The optional property assistant must distinguish *available* from *locked*. It must not silently populate operating-condition viscosity or IFT without explicit user action.
- Prediction results should present the D50 hero, separate Re/We/Ca tiles, selected calibration provenance, and a clearly separated field-scale extrapolation notice. Never label a field-scale extrapolation as validated.
- The `Predict D50` button may display `Calculating…` while an asynchronous worker runs. Do not block the UI thread, use artificial progress delays, or show stale results.
- Smooth scrolling should not steal focus or jump to inaccessible widgets during expanding/collapsing layouts. Avoid dereferencing Qt wrappers after their underlying C++ objects have been deleted.
- The ~1,900-line SSDI view needs incremental extraction. See `SSDI_GUI_REFACTORING_PLAN.md` for target boundaries; do not use styling changes as a pretext for a large behavioural rewrite.
- **Typography note:** this document's values have been aligned to the actual `TYPOGRAPHY` constants in the shared `theme.py` snapshot inspected on 2026-10-19. Recheck if that file changes.
