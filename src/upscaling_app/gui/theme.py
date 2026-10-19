"""Shared design tokens for the Upscaling App PySide6 desktop interface.

Sizes use logical Qt pixels. The operating system remains responsible for DPI
scaling; the user-selected text scale is applied on top of that baseline.
"""

from string import Template

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32,
    "huge": 48,
    "massive": 64,
}

# Font size, target line height (Qt Style Sheets have no CSS line-height).
TYPOGRAPHY = {
    "h1": (32, 40),
    "h2": (28, 36),
    "h3": (20, 28),
    "body_lg": (18, 28),
    "body_md": (16, 24),
    "body_sm": (14, 20),
    "caption": (12, 16),
}

TEXT_SCALES = (100, 125, 150)
DEFAULT_TEXT_SCALE = 100

COLORS = {
    "background": "#F4F6FA",
    "surface": "#FFFFFF",
    "surface_subtle": "#F8FAFC",
    "sidebar": "#111827",
    "sidebar_active": "#293449",
    "text": "#172033",
    "text_muted": "#475569",
    "text_soft": "#526179",
    "sidebar_secondary": "#CBD5E1",
    "sidebar_tertiary": "#B3C2D6",
    "border": "#D5DCE7",
    "accent": "#F97316",
    "accent_light": "#FFF0E6",
    "accent_deep": "#9A440A",
    "success": "#145A37",
    "success_light": "#E4F6EC",
}

RADIUS = {"sm": 8, "md": 12, "lg": 16}


def scaled_space(token: str, scale: int) -> int:
    """Keep spaces/paddings aligned to a 4-logical-pixel grid."""
    if scale not in TEXT_SCALES:
        raise ValueError(f"Unsupported text scale: {scale}")
    return max(4, 4 * round(SPACING[token] * scale / 400))


def scaled_type(token: str, scale: int) -> tuple[int, int]:
    if scale not in TEXT_SCALES:
        raise ValueError(f"Unsupported text scale: {scale}")
    size, height = TYPOGRAPHY[token]
    return round(size * scale / 100), round(height * scale / 100)


_QSS = Template("""
QWidget#header {
    background-color: $background;
}
QWidget#window, QWidget#body {
    background-color: $background;
    color: $text;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: ${body_md}px;
}
QScrollArea {
    background-color: $background;
    border: none;
}
QFrame#sidebar {
    background-color: $sidebar;
    border: none;
}
QLabel {
    background: transparent;
    color: $text;
}
QLabel#logo {
    background-color: $accent;
    color: white;
    border-radius: ${radius_sm}px;
    font-size: ${h3}px;
    font-weight: 700;
}
QLabel#brand {
    color: white;
    font-size: ${body_lg}px;
    font-weight: 700;
}
QLabel#sideSubtitle, QLabel#inactiveNav {
    color: $sidebar_secondary;
    font-size: ${body_sm}px;
}
QLabel#navHeading, QLabel#sideFooter {
    color: $sidebar_tertiary;
    font-size: ${body_sm}px;
}
QLabel#activeNav {
    color: white;
    background-color: $sidebar_active;
    border-left: 4px solid $accent;
    border-radius: ${radius_sm}px;
    font-size: ${body_md}px;
    font-weight: 700;
    padding: ${space_md}px ${space_lg}px;
}
QLabel#breadcrumb {
    color: $text_muted;
    font-size: ${body_sm}px;
    font-weight: 700;
}
QLabel#status {
    color: $success;
    background-color: $success_light;
    border: 1px solid #B5DEC7;
    border-radius: ${radius_md}px;
    padding: ${space_sm}px ${space_md}px;
    font-size: ${body_sm}px;
    font-weight: 700;
}
QLabel#title {
    color: $text;
    font-size: ${h1}px;
    font-weight: 700;
}
QLabel#subtitle {
    color: $text_muted;
    font-size: ${body_md}px;
}
QFrame#card {
    background-color: $surface;
    border: 1px solid $border;
    border-radius: ${radius_lg}px;
}
QLabel#cardTitle {
    color: $text;
    font-size: ${h3}px;
    font-weight: 700;
}
QLabel#cardSubtitle, QLabel#description {
    color: $text_muted;
    font-size: ${body_md}px;
}
QLabel#fieldLabel {
    color: $text;
    font-size: ${body_sm}px;
    font-weight: 700;
}

QLineEdit#fieldInput {
    background-color: $surface_subtle;
    color: $text;
    border: 1px solid $border;
    border-radius: ${radius_sm}px;
    padding: ${space_sm}px ${space_md}px;
    font-size: ${body_md}px;
}
QLineEdit#fieldInput:hover {
    border-color: $accent;
}

QLineEdit#fieldInput:focus {
    background-color: $surface;
    border: 2px solid $accent;
}
QPushButton#modelOption {
    background-color: $surface_subtle;
    color: $text;
    border: 1px solid $border;
    border-radius: ${radius_sm}px;
    padding: ${space_md}px ${space_sm}px;
    min-height: ${model_min_height}px;
    font-size: ${body_md}px;
    font-weight: 600;
}
QPushButton#modelOption:hover {
    background-color: $accent_light;
    border-color: $accent;
}
QPushButton#modelOption:checked {
    background-color: $accent_light;
    border: 2px solid $accent;
    color: $accent_deep;
    font-weight: 700;
}
QPushButton#modelOption:disabled {
    background-color: #EEF1F5;
    color: $text_soft;
    border: 1px dashed $border;
}
QPushButton#modelOption:focus {
    border: 2px solid $accent;
}
QLabel#scaleLabel {
    color: $text_muted;
    font-size: ${body_sm}px;
    font-weight: 700;
}
QPushButton#fontScale {
    background-color: $surface;
    color: $text;
    border: 1px solid #B4C0D0;
    border-radius: ${radius_sm}px;
    padding: ${space_sm}px ${space_md}px;
    min-height: ${scale_min_height}px;
    font-size: ${body_sm}px;
    font-weight: 700;
}
QPushButton#fontScale:hover {
    background-color: $accent_light;
    border-color: $accent;
}
QPushButton#fontScale:checked {
    background-color: $accent_light;
    color: $accent_deep;
    border: 2px solid $accent;
}
QPushButton#fontScale:focus:!checked {
    border: 2px solid $text_muted;
}
QPushButton#registerOil {
    background-color: $accent_light;
    color: $accent_deep;
    border: 1px solid $accent;
    border-radius: ${radius_sm}px;
    padding: ${space_sm}px ${space_lg}px;
    font-size: ${body_md}px;
    font-weight: 700;
}
QPushButton#registerOil:hover {
    border: 2px solid $accent;
}

QFrame#comingSoonBanner {
    background-color: $accent_light;
    border: 1px solid $accent;
    border-radius: ${radius_sm}px;
}
QPushButton#noticeDismiss {
    background-color: transparent;
    color: $accent_deep;
    border: none;
    font-size: ${body_md}px;
    font-weight: 700;
}
QPushButton#noticeDismiss:hover {
    background-color: $surface;
    border-radius: ${radius_sm}px;
}
QPushButton#viscosityEstimate {
    background-color: $accent_light;
    color: $accent_deep;
    border: 1px solid $accent;
    border-radius: ${radius_sm}px;
    padding: ${space_sm}px ${space_md}px;
    font-size: ${body_sm}px;
    font-weight: 700;
}
QPushButton#viscosityEstimate:hover {
    background-color: $accent;
    color: white;
}

QPushButton#viscosityEstimate:pressed {
    background-color: $accent_deep;
    color: white;
}
QPushButton#viscosityEstimate:focus {
    border: 2px solid $accent_deep;
}
QFrame#metric {
    background-color: $surface_subtle;
    border: 1px solid $border;
    border-radius: ${radius_md}px;
}
QLabel#metricName, QLabel#metricHint {
    color: $text_muted;
    font-size: ${body_sm}px;
}
QLabel#metricName { font-weight: 700; }
QLabel#metricValue {
    color: $text;
    font-size: ${h2}px;
    font-weight: 700;
}
QLabel#note {
    color: $text_soft;
    font-size: ${body_sm}px;
}
QLabel#nextTitle {
    color: $text;
    font-size: ${body_lg}px;
    font-weight: 700;
}
QLabel#nextBody {
    color: $text_muted;
    font-size: ${body_md}px;
}
QLabel#step {
    color: $accent_deep;
    background-color: $accent_light;
    border-radius: ${radius_sm}px;
    padding: ${space_sm}px ${space_md}px;
    font-size: ${body_sm}px;
    font-weight: 700;
}

QLabel#assistantIcon {
    color: $text_muted;
    font-size: ${h3}px;
}

QLabel#assistantSubtitle {
    color: $text_muted;
    font-size: ${body_sm}px;
}

QPushButton#propertyAssistantToggle {
    background-color: transparent;
    color: $text;
    border: none;
    padding: 0;
    font-size: ${body_lg}px;
    font-weight: 700;
    text-align: left;
}

QPushButton#propertyAssistantToggle:hover {
    color: $accent_deep;
}

QPushButton#propertyAssistantToggle:focus {
    border: 1px solid $accent;
    border-radius: ${radius_sm}px;
}

QPushButton#propertyAssistantArrow {
    background-color: transparent;
    color: $text_muted;
    border: none;
    font-size: ${h3}px;
    font-weight: 700;
}

QPushButton#propertyAssistantArrow:hover {
    color: $accent_deep;
}

QPushButton#propertyAssistantArrow:focus {
    border: 1px solid $accent;
    border-radius: ${radius_sm}px;
}

QFrame#optionalSection {
    background-color: $surface_subtle;
    border: 1px solid $border;
    border-radius: ${radius_md}px;
}


QPushButton#iftOption {
    background-color: $surface;
    color: $text;
    border: 1px solid $border;
    border-radius: ${radius_sm}px;
    padding: ${space_md}px ${space_sm}px;
    font-size: ${body_sm}px;
    font-weight: 600;
}

QPushButton#iftOption:hover {
    border-color: $accent;
}

QPushButton#iftOption:checked {
    background-color: $accent_light;
    border: 2px solid $accent;
    color: $accent_deep;
}

QPushButton#iftUseReference {
    background-color: $accent_light;
    color: $accent_deep;
    border: 1px solid $accent;
    border-radius: ${radius_sm}px;
    padding: ${space_sm}px ${space_lg}px;
    font-size: ${body_sm}px;
    font-weight: 700;
}

QPushButton#iftUseReference:hover {
    background-color: $accent;
    color: white;
}

QPushButton#iftUseReference:disabled {
    background-color: $surface_subtle;
    color: $text_muted;
    border-color: $border;
}

QPushButton#propertyAssistantToggle:disabled,
QPushButton#propertyAssistantArrow:disabled {
    color: $text_muted;
}

QFrame#propertyAssistant {
    border-radius: ${radius_md}px;
}

QFrame#propertyAssistant[assistantState="locked"] {
    background-color: #EEF1F5;
    border: 1px solid $border;
}

QFrame#propertyAssistant[assistantState="available"] {
    background-color: $surface;
    border: 1px solid $accent;
    border-left: 4px solid $accent;
}

QLabel#assistantStatus {
    font-size: ${caption}px;
    font-weight: 700;
    border-radius: ${radius_sm}px;
    padding: ${space_xs}px ${space_sm}px;
}

QLabel#assistantStatus[assistantState="locked"] {
    background-color: #E2E8F0;
    color: $text_muted;
}

QLabel#assistantStatus[assistantState="available"] {
    background-color: $accent_light;
    color: $accent_deep;
}

QPushButton#propertyAssistantToggle:enabled {
    color: $text;
}

QPushButton#propertyAssistantToggle:disabled {
    color: $text_muted;
}

QPushButton#propertyAssistantArrow:enabled {
    color: $accent_deep;
}

QPushButton#propertyAssistantArrow:disabled {
    color: $text_muted;
}

QPushButton#predictD50 {
    background-color: $accent;
    color: white;
    border: 1px solid $accent;
    border-radius: ${radius_sm}px;
    padding: ${space_md}px ${space_xl}px;
    font-size: ${body_md}px;
    font-weight: 700;
}

QPushButton#predictD50:hover {
    background-color: $accent_deep;
    border-color: $accent_deep;
}

QPushButton#predictD50:pressed {
    background-color: $accent_deep;
}

QLabel#predictionError {
    background-color: $accent_light;
    color: $accent_deep;
    border: 1px solid $accent;
    border-radius: ${radius_sm}px;
    padding: ${space_md}px;
    font-size: ${body_sm}px;
}

/* Main prediction result */
QFrame#predictionHero {
    background-color: $surface_subtle;
    border: 1px solid $border;
    border-radius: ${radius_md}px;
}

QLabel#predictionEyebrow {
    color: $text_muted;
    font-size: ${body_sm}px;
    font-weight: 700;
}

QLabel#predictionValue {
    color: $text;
    font-size: ${h1}px;
    font-weight: 700;
}

QLabel#predictionMeta {
    color: $text_muted;
    font-size: ${body_sm}px;
}

/* Dimensionless groups */
QFrame#predictionMetric {
    background-color: $surface;
    border: 1px solid $border;
    border-radius: ${radius_md}px;
}

QLabel#predictionMetricName {
    color: $text_muted;
    font-size: ${body_sm}px;
}

QLabel#predictionMetricValue {
    color: $text;
    font-size: ${h2}px;
    font-weight: 700;
}

/* Scientific applicability warning */
QFrame#predictionWarningFrame {
    background-color: $accent_light;
    border: 1px solid $accent;
    border-left: 4px solid $accent;
    border-radius: ${radius_sm}px;
}

QLabel#predictionWarningTitle {
    color: $accent_deep;
    font-size: ${body_sm}px;
    font-weight: 700;
}

QLabel#predictionWarningText {
    color: $text_soft;
    font-size: ${body_sm}px;
}
QPushButton#predictD50:disabled {
    background-color: $accent_light;
    color: $accent_deep;
    border: 1px solid $accent;
}
""")


def build_stylesheet(scale: int = DEFAULT_TEXT_SCALE) -> str:
    """Render a consistent stylesheet for a selected accessibility scale."""
    if scale not in TEXT_SCALES:
        raise ValueError(f"Unsupported text scale: {scale}")
    tokens = {
        **COLORS,
        **{name: scaled_type(name, scale)[0] for name in TYPOGRAPHY},
        **{f"space_{name}": scaled_space(name, scale) for name in SPACING},
        **{f"radius_{name}": value for name, value in RADIUS.items()},
        "model_min_height": scaled_space("xl", scale),
        "scale_min_height": scaled_space("lg", scale),
    }
    return _QSS.substitute(tokens)
