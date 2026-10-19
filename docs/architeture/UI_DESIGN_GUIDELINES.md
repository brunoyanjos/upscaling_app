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

## Desktop typography and accessibility

Typography tokens are defined in `upscaling_app.gui.theme` and interpreted as
logical Qt pixels before the user's text-scale preference is applied.

| Token | Base font size | Target line height | Primary use |
| --- | ---: | ---: | --- |
| `h1` | 32 px | 40 px | Screen title |
| `h2` | 28 px | 36 px | Large result value |
| `h3` | 20 px | 28 px | Card title |
| `body_lg` | 18 px | 28 px | Emphasized prose |
| `body_md` | 16 px | 24 px | Standard text and controls |
| `body_sm` | 14 px | 20 px | Secondary labels, notes |
| `caption` | 12 px | 16 px | Nonessential detail |

The user can select **100%, 125%, or 150%** text size. The default 100% must
already be legible. Use `build_stylesheet(scale)`, `scaled_type()` and
`scaled_space()` from `gui/theme.py` rather than manually scaling fonts in views.
Spacing, paddings and widget dimensions should still align to the 4-pixel grid.

The desktop preference is persisted using `QSettings("UpscalingApp", "UpscalingApp")`
with the key `accessibility/text_scale`. A view must preserve form state when
reapplying an accessibility scale; never reset a user's scientific inputs.

The window content must reflow or scroll gracefully at 150%. Avoid fixed heights
for text-heavy labels, and use word wrapping. The operating system handles
screen DPI scaling; do not forcibly disable or override it.

The palette should use dark, high-contrast text on light backgrounds and clearly
readable sidebar labels. Selected, hover, focus and disabled states must be
visually distinct. Test with actual Windows, WSLg/Linux and macOS scaling.

**Qt limitation:** Qt Style Sheets do not implement web CSS `line-height`. The
listed line heights are layout targets, not CSS properties.

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
