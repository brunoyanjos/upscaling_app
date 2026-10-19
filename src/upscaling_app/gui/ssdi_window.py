"""SSDI calibration selection with accessible, persistent text scaling.

Run from the repository root:
    python -m upscaling_app.gui.ssdi_window
"""

import os
import sys
from pathlib import Path

# The GUI performs scalar inference and does not require CUDA.
# Must be configured before importing JAX or modules that use JAX.
os.environ["JAX_PLATFORMS"] = "cpu"

from upscaling_app import paths
import numpy as np

from shiboken6 import isValid

from PySide6.QtCore import (
    QSettings,
    Qt,
    QLocale,
    QPoint,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QThread,
    Signal,
)
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QLineEdit,
)

from upscaling_app.upscaling.ssdi.io.data import (
    IFT_UNVERIFIED_OILS,
    load_ift_references,
    load_oil_properties,
)

from upscaling_app.gui.theme import (
    DEFAULT_TEXT_SCALE,
    TEXT_SCALES,
    build_stylesheet,
    scaled_space,
    scaled_type,
)
from upscaling_app.upscaling.ssdi.model_catalog import (
    MODEL_NAMES,
    load_global_calibrations,
    load_oil_wise_calibrations,
)

from upscaling_app.upscaling.ssdi.physics.viscosity import (
    estimate_stabilized_viscosity,
)
from upscaling_app.upscaling.ssdi.prediction import (
    predict_field_ssdi,
)

MODEL_DESCRIPTIONS = {
    "sintef_baseline": "Original SINTEF reference parameters.",
    "jax_baseline_all": "Global calibration using the full population of 10 oils.",
    "jax_exclude_3016_4662_4665": (
        "Calibration based on the selected population of 7 oils. "
        "Its validation results do not automatically generalize to other oils."
    ),
}


class PredictionWorker(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, scenario, a, b, parent=None):
        super().__init__(parent)
        self.scenario = scenario
        self.a = a
        self.b = b

    def run(self):
        try:
            result = predict_field_ssdi(
                scenario=self.scenario,
                a=self.a,
                b=self.b,
            )
        except Exception as error:
            self.failed.emit(str(error))
        else:
            self.completed.emit(result)


class SSDIWindow(QWidget):
    def __init__(
        self,
        calibrations: dict[str, tuple[float, float]],
        oils,
        ift_references,
        oil_wise_calibrations: dict[int, tuple[float, float]],
    ) -> None:
        super().__init__()
        self.calibrations = calibrations
        self.oil_wise_calibrations = oil_wise_calibrations

        self.oils = oils
        self.selected_oil_id = None
        self.property_assistant_expanded = False

        self.ift_references = ift_references
        self.selected_ift_treatment = "untreated"
        self.ift_was_applied = False

        self.selected_model = "jax_baseline_all"
        self.settings = QSettings("UpscalingApp", "UpscalingApp")
        saved_scale = self.settings.value(
            "accessibility/text_scale", DEFAULT_TEXT_SCALE, type=int
        )
        self.text_scale = (
            saved_scale if saved_scale in TEXT_SCALES else DEFAULT_TEXT_SCALE
        )
        self.model_buttons: dict[str, QPushButton] = {}
        self.scale_buttons: dict[int, QPushButton] = {}
        self.model_button_group: QButtonGroup | None = None
        self.scale_button_group: QButtonGroup | None = None

        self.setObjectName("window")
        self.setWindowTitle("Upscaling App | SSDI Prediction")
        self.resize(1120, 760)
        self.setMinimumSize(920, 620)

        self.root_layout = QHBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.field_values = {
            "nozzle_diameter": "470",
            "oil_flow": "12000",
            "gor": "0.9",
            "gas_density": "",
            "oil_density": "",
            "oil_viscosity": "",
            "ift": "",
            "oil_temperature": "",
        }

        self.field_inputs: dict[str, QLineEdit] = {}

        self._prediction_worker = None

        self._render()

    def _space(self, name: str) -> int:
        return scaled_space(name, self.text_scale)

    def _label(self, text: str, role: str, *, wrap: bool = False) -> QLabel:
        widget = QLabel(text)
        widget.setObjectName(role)
        widget.setWordWrap(wrap)
        role_to_font = {
            "brand": "body_lg",
            "title": "h1",
            "cardTitle": "h3",
            "metricValue": "h2",
            "nextTitle": "body_lg",
            "subtitle": "body_md",
            "cardSubtitle": "body_md",
            "description": "body_md",
            "nextBody": "body_md",
        }
        font_role = role_to_font.get(role)
        if font_role:
            widget.setMinimumHeight(scaled_type(font_role, self.text_scale)[1])
        return widget

    def _metric(self, name: str, hint: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setObjectName("metric")
        layout = QVBoxLayout(card)
        margin = self._space("lg")
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(self._space("sm"))
        layout.addWidget(self._label(name, "metricName"))
        value = self._label("—", "metricValue")
        layout.addWidget(value)
        layout.addWidget(self._label(hint, "metricHint"))
        return card, value

    def _render(self) -> None:
        """Recreate geometry at the new text scale, preserving model selection."""

        application = QApplication.instance()
        if application is not None:
            application.setStyleSheet(build_stylesheet(self.text_scale))

        if self.model_button_group is not None:
            self.model_button_group.deleteLater()
        if self.scale_button_group is not None:
            self.scale_button_group.deleteLater()

        self.field_values.update(
            {key: editor.text() for key, editor in self.field_inputs.items()}
        )

        self.field_inputs.clear()
        self.prediction_result = None

        while self.root_layout.count():
            item = self.root_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        self.model_buttons = {}
        self.scale_buttons = {}
        self.model_button_group = QButtonGroup(self)
        self.model_button_group.setExclusive(True)
        self.scale_button_group = QButtonGroup(self)
        self.scale_button_group.setExclusive(True)

        self.root_layout.addWidget(self._build_sidebar())

        main_panel = QWidget()
        main_panel.setObjectName("body")

        main_layout = QVBoxLayout(main_panel)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Fixed header
        main_layout.addWidget(self._build_header())

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(self._build_body())

        self.content_scroll = scroll

        main_layout.addWidget(scroll, 1)

        self.root_layout.addWidget(main_panel, 1)

        self._update_oil_wise_availability()

        self.model_buttons[self.selected_model].setChecked(True)
        self.scale_buttons[self.text_scale].setChecked(True)
        self.update_coefficients()

        QTimer.singleShot(
            0,
            lambda: self.scale_buttons[self.text_scale].setFocus(
                Qt.FocusReason.OtherFocusReason
            ),
        )

    def _build_sidebar(self) -> QFrame:
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth({100: 240, 125: 280, 150: 320}[self.text_scale])
        layout = QVBoxLayout(side)
        layout.setContentsMargins(
            self._space("xl"),
            self._space("xxl"),
            self._space("xl"),
            self._space("xl"),
        )
        layout.setSpacing(0)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(self._space("md"))
        logo = self._label("U", "logo")
        logo_side = self._space("xxl") + self._space("sm")
        logo.setFixedSize(logo_side, logo_side)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_row.addWidget(logo)

        brand_column = QVBoxLayout()
        brand_column.setSpacing(self._space("xs"))
        brand_column.addWidget(self._label("UPSCALING", "brand"))
        brand_column.addWidget(
            self._label("SCIENTIFIC TOOLKIT", "sideSubtitle", wrap=True)
        )
        brand_row.addLayout(brand_column, 1)
        layout.addLayout(brand_row)

        layout.addSpacing(self._space("huge"))
        layout.addWidget(self._label("MODELLING", "navHeading"))
        layout.addSpacing(self._space("lg"))
        layout.addWidget(self._label("SSDI  /  Prediction", "activeNav", wrap=True))
        layout.addSpacing(self._space("sm"))
        layout.addWidget(self._label("SSMD  ·  Coming later", "inactiveNav", wrap=True))
        layout.addSpacing(self._space("lg"))
        layout.addWidget(
            self._label("Distributions  ·  Coming later", "inactiveNav", wrap=True)
        )
        layout.addStretch()
        layout.addWidget(
            self._label("Research application  ·  v0.1", "sideFooter", wrap=True)
        )
        return side

    def _build_scale_controls(self) -> QHBoxLayout:
        controls = QHBoxLayout()
        controls.setSpacing(self._space("sm"))
        controls.addWidget(self._label("Text size", "scaleLabel"))
        controls.addSpacing(self._space("sm"))

        for scale in TEXT_SCALES:
            button = QPushButton(f"{scale}%")
            button.setObjectName("fontScale")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setAccessibleName(f"Text size {scale} percent")
            button.setToolTip(f"Display text at {scale}% of the base size")
            button.setMinimumHeight(self._space("xxl"))
            self.scale_button_group.addButton(button)
            self.scale_buttons[scale] = button
            button.clicked.connect(
                lambda _checked=False, value=scale: self.change_text_scale(value)
            )
            controls.addWidget(button)
        return controls

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("header")

        layout = QVBoxLayout(header)
        margin = self._space("xxl")

        layout.setContentsMargins(
            margin,
            self._space("lg"),
            margin,
            self._space("lg"),
        )
        layout.setSpacing(0)

        top = QHBoxLayout()
        top.setSpacing(self._space("lg"))

        top.addWidget(self._label("MODELLING   /   SSDI", "breadcrumb"))
        top.addStretch()
        top.addWidget(
            self._label(
                f"●  {len(MODEL_NAMES)} CALIBRATION MODES",
                "status",
            )
        )

        layout.addLayout(top)

        layout.addSpacing(self._space("lg"))

        scale_row = QHBoxLayout()
        scale_row.addStretch()
        scale_row.addLayout(self._build_scale_controls())

        layout.addLayout(scale_row)

        layout.addSpacing(self._space("xl"))

        layout.addWidget(
            self._label(
                "Field-scale prediction",
                "title",
                wrap=True,
            )
        )

        layout.addSpacing(self._space("sm"))

        layout.addWidget(
            self._label(
                "Configure the SSDI correlation using "
                "persisted calibration parameters.",
                "subtitle",
                wrap=True,
            )
        )

        return header

    def _animate_oil_scroll(self, target: int, on_finish=None) -> None:
        scrollbar = self.content_scroll.verticalScrollBar()

        target = max(0, min(int(target), scrollbar.maximum()))

        previous = getattr(self, "_oil_scroll_animation", None)

        if previous is not None and isValid(previous):
            previous.stop()
            previous.deleteLater()

        if target == scrollbar.value():
            if on_finish is not None:
                on_finish()
            return

        animation = QPropertyAnimation(scrollbar, b"value", self)
        animation.setDuration(280)
        animation.setStartValue(scrollbar.value())
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if on_finish is not None:
            animation.finished.connect(on_finish)

        self._oil_scroll_animation = animation
        animation.start()

    def _collapse_oil_picker(self) -> None:
        panel = self.oil_picker_panel

        self.oil_search.clearFocus()

        previous = getattr(self, "_oil_picker_height_animation", None)

        if previous is not None:
            previous.stop()
            previous.deleteLater()

        animation = QPropertyAnimation(panel, b"maximumHeight", self)

        animation.setDuration(300)
        animation.setStartValue(panel.height())
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def finish() -> None:
            panel.hide()
            panel.setMaximumHeight(16777215)

            QTimer.singleShot(
                0,
                self._scroll_to_selected_oil,
            )

        animation.finished.connect(finish)

        self._oil_picker_height_animation = animation
        animation.start()

    def _scroll_to_selected_oil(self) -> None:
        content = self.content_scroll.widget()
        if content is None:
            return

        position = self.oil_select_button.mapTo(content, QPoint(0, 0))

        # Show the selected oil and surrounding properties.
        target = position.y() - 3 * self._space("xxl")

        self._animate_oil_scroll(
            target,
            on_finish=lambda: self.oil_select_button.setFocus(
                Qt.FocusReason.OtherFocusReason
            ),
        )

    def _toggle_oil_selector(self) -> None:
        if self.oil_picker_panel.isVisible():
            self._collapse_oil_picker()
            return

        self.oil_picker_panel.show()

        QTimer.singleShot(
            0,
            self._scroll_to_oil_picker,
        )

    def _scroll_to_oil_picker(self) -> None:
        content = self.content_scroll.widget()
        if content is None:
            return

        scrollbar = self.content_scroll.verticalScrollBar()
        viewport_height = self.content_scroll.viewport().height()

        search_y = self.oil_search.mapTo(content, QPoint(0, 0)).y()

        margin = self._space("lg")

        # Keep the search input and approximately two choices visible.
        required_bottom = (
            search_y
            + self.oil_search.height()
            + 2 * self._space("huge")
            + self._space("md")
        )

        current = scrollbar.value()

        if search_y < current + margin:
            target = search_y - margin
        elif required_bottom > current + viewport_height - margin:
            target = required_bottom - viewport_height + margin
        else:
            target = current

        self._animate_oil_scroll(
            target,
            on_finish=lambda: (
                self.oil_search.setFocus()
                if self.oil_picker_panel.isVisible()
                else None
            ),
        )

    def _filter_oil_options(self, search: str) -> None:
        query = search.strip().casefold()

        for button in self.oil_option_buttons.values():
            button.setVisible(query in button.text().casefold())

    def _select_oil(
        self,
        oil_id: int | None,
    ) -> None:
        changed = oil_id != self.selected_oil_id

        self.selected_oil_id = oil_id

        self.oil_select_button.setText(self.oil_labels[oil_id] + "  ▾")

        for current_id, button in self.oil_option_buttons.items():
            button.setChecked(current_id == oil_id)

        self._collapse_oil_picker()
        self.oil_search.clear()

        self.oil_reference_label.setText(self._oil_reference_text(oil_id))
        self._update_ift_reference()
        self._update_property_assistant_availability()

        self._update_oil_wise_availability()

        self.model_buttons[self.selected_model].setChecked(True)
        self.update_coefficients()

        # Do not discard edited values if the same oil is reselected.
        if not changed:
            return

        self._invalidate_prediction()

        # Prevent properties from a previous oil being reused.
        values = {
            "oil_density": "",
            "oil_viscosity": "",
            "ift": "",
        }

        self.ift_was_applied = False

        if oil_id is not None:
            oil = self.oils.loc[self.oils["oil_id"] == oil_id]

            if len(oil) != 1:
                raise ValueError(f"Expected one registered oil: {oil_id}")

            values["oil_density"] = f"{float(oil.iloc[0]['density']):g}"

        self.field_values.update(values)

        for key, value in values.items():
            self.field_inputs[key].setText(value)

    def _build_oil_selector(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self._space("sm"))

        layout.addWidget(self._label("SELECT OIL", "fieldLabel"))

        options = [(None, "Custom oil")]

        options.extend(
            (
                int(oil.oil_id),
                f"{oil.oil_id} — {oil.oil_name}",
            )
            for oil in self.oils.itertuples(index=False)
        )

        self.oil_labels = dict(options)

        self.oil_select_button = QPushButton(
            self.oil_labels.get(self.selected_oil_id, "Custom oil") + "  ▾"
        )
        self.oil_select_button.setObjectName("modelOption")
        self.oil_select_button.setMinimumHeight(self._space("huge"))
        self.oil_select_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.oil_select_button.clicked.connect(self._toggle_oil_selector)

        layout.addWidget(self.oil_select_button)

        # Expandable selection panel
        self.oil_picker_panel = QFrame()
        self.oil_picker_panel.setObjectName("metric")

        panel_layout = QVBoxLayout(self.oil_picker_panel)
        margin = self._space("lg")
        panel_layout.setContentsMargins(margin, margin, margin, margin)
        panel_layout.setSpacing(self._space("md"))

        self.oil_search = QLineEdit()
        self.oil_search.setObjectName("fieldInput")
        self.oil_search.setPlaceholderText("Search by oil ID or name...")
        self.oil_search.setMinimumHeight(self._space("huge"))
        self.oil_search.textChanged.connect(self._filter_oil_options)

        panel_layout.addWidget(self.oil_search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMaximumHeight(self._space("huge") * 6)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(self._space("sm"))

        self.oil_option_buttons = {}

        for oil_id, label in options:
            button = QPushButton(label)
            button.setObjectName("modelOption")
            button.setCheckable(True)
            button.setChecked(oil_id == self.selected_oil_id)
            button.setMinimumHeight(self._space("huge"))
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )
            button.setCursor(Qt.CursorShape.PointingHandCursor)

            button.clicked.connect(
                lambda checked=False, value=oil_id: self._select_oil(value)
            )

            self.oil_option_buttons[oil_id] = button
            options_layout.addWidget(button)

        options_layout.addStretch()
        scroll.setWidget(options_widget)
        panel_layout.addWidget(scroll)

        self.oil_picker_panel.hide()
        layout.addWidget(self.oil_picker_panel)

        return container

    def _dismiss_register_notice(self) -> None:
        self.register_banner.hide()

        QTimer.singleShot(
            0,
            lambda: self.register_button.setFocus(Qt.FocusReason.OtherFocusReason),
        )

    def _show_register_notice(self) -> None:
        self.register_banner.show()

        QTimer.singleShot(
            0,
            lambda: self.content_scroll.ensureWidgetVisible(
                self.register_banner,
                0,
                self._space("lg"),
            ),
        )

    def _oil_reference_text(
        self,
        oil_id: int | None,
    ) -> str:
        if oil_id is None:
            return "Custom oil — enter the properties manually."

        oil = self.oils.loc[self.oils["oil_id"] == oil_id]

        if len(oil) != 1:
            raise ValueError(f"Expected one registered oil: {oil_id}")

        record = oil.iloc[0]

        mu20 = float(record["dynamic_viscosity_20c_est"]) * 1e3
        mu40 = float(record["dynamic_viscosity_40c_est"]) * 1e3
        mu50 = float(record["dynamic_viscosity_50c_est"]) * 1e3

        return (
            "Estimated dynamic viscosity — "
            f"20°C: {mu20:.2f} mPa·s  |  "
            f"40°C: {mu40:.2f} mPa·s  |  "
            f"50°C: {mu50:.2f} mPa·s.  "
            "Estimated using density at 15°C. "
            "Enter the viscosity at release conditions."
        )

    def _use_estimated_viscosity(self) -> None:
        if self.selected_oil_id is None:
            self.viscosity_note.setText(
                "Select a registered oil to estimate viscosity."
            )
            return

        temperature_text = self.field_inputs["oil_temperature"].text().strip()

        try:
            temperature_c = float(temperature_text)
        except ValueError:
            self.viscosity_note.setText("Enter a valid oil temperature.")
            return

        oil = self.oils.loc[self.oils["oil_id"] == self.selected_oil_id]

        if len(oil) != 1:
            self.viscosity_note.setText("Registered oil properties not found.")
            return

        record = oil.iloc[0]

        viscosities = tuple(
            float(record[f"dynamic_viscosity_{t}c_est"]) for t in (20, 40, 50)
        )

        try:
            mu = estimate_stabilized_viscosity(
                temperature_c=temperature_c,
                viscosities_pa_s=viscosities,
            )
        except ValueError as error:
            self.viscosity_note.setText(str(error))
            return

        mu_mpas = mu * 1e3

        self.field_inputs["oil_viscosity"].setText(f"{mu_mpas:.4f}")

        self.viscosity_note.setText(
            f"Estimated viscosity at {temperature_c:g}°C: "
            f"{mu_mpas:.4f} mPa·s. "
            "Stabilized-oil estimate, using reference "
            "viscosities derived with density at 15°C. "
            "Not corrected for dissolved gas."
        )

    def _scroll_to_property_assistant(self) -> None:
        content = self.content_scroll.widget()

        if content is None:
            return

        position = self.property_assistant_toggle.mapTo(
            content,
            QPoint(0, 0),
        )

        scrollbar = self.content_scroll.verticalScrollBar()

        target = max(
            0,
            position.y() - self._space("lg"),
        )

        target = min(target, scrollbar.maximum())

        previous = getattr(
            self,
            "_assistant_scroll_animation",
            None,
        )

        if previous is not None:
            previous.stop()
            previous.deleteLater()

        self._assistant_scroll_animation = QPropertyAnimation(
            scrollbar,
            b"value",
            self,
        )

        animation = self._assistant_scroll_animation

        animation.setDuration(280)
        animation.setStartValue(scrollbar.value())
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        animation.start()

    def _toggle_property_assistant(self) -> None:
        if self.selected_oil_id is None:
            return

        self.property_assistant_expanded = not self.property_assistant_expanded

        expanded = self.property_assistant_expanded

        self.property_assistant_content.setVisible(expanded)
        self.property_assistant_arrow.setText("▾" if expanded else "▸")

        self.property_assistant_toggle.setAccessibleName(
            "Collapse property assistant" if expanded else "Expand property assistant"
        )

        if expanded:
            QTimer.singleShot(
                0,
                self._scroll_to_property_assistant,
            )

    def _update_ift_reference(self) -> None:
        oil_id = self.selected_oil_id

        self.ift_use_button.setEnabled(False)

        if oil_id is None:
            self.ift_preview.setText(
                "Select a registered oil to view laboratory references."
            )
            return

        if oil_id in IFT_UNVERIFIED_OILS:
            self.ift_preview.setText(
                "Source discrepancy detected for this oil. "
                "Automatic IFT reference use is temporarily disabled."
            )
            return

        key = (oil_id, self.selected_ift_treatment)
        ift = self.ift_references.get(key)

        if ift is None:
            self.ift_preview.setText("No laboratory reference for this treatment.")
            return

        ift_mnm = ift * 1e3

        condition = (
            "Untreated oil, seawater, 50°C"
            if self.selected_ift_treatment == "untreated"
            else "1% dispersant premixed in oil, seawater, 50°C"
        )

        self.ift_preview.setText(f"Laboratory IFT: {ift_mnm:.4g} mN/m  ·  {condition}")

        self.ift_use_button.setEnabled(True)

    def _update_oil_wise_availability(self) -> None:
        oil_id = self.selected_oil_id

        available = oil_id is not None and oil_id in self.oil_wise_calibrations

        button = self.model_buttons["jax_oil_wise"]
        button.setEnabled(available)

        if oil_id is None:
            button.setText("Oil-wise · Locked")
            message = "Select a registered oil to enable " "the Oil-wise calibration."
        elif not available:
            button.setText("Oil-wise · Locked")
            message = "No persisted Oil-wise calibration " "is available for this oil."
        else:
            button.setText(f"Oil-wise · {oil_id}")
            message = (
                f"Oil-wise calibration available for "
                f"{self.oil_labels[oil_id]}. "
                "Coefficients fitted to this oil only."
            )

        self.model_availability_note.setText(message)

        if not available and self.selected_model == "jax_oil_wise":
            self.selected_model = "jax_baseline_all"

    def _select_ift_treatment(self, treatment: str) -> None:
        if treatment != self.selected_ift_treatment:
            if self.ift_was_applied:
                self.field_inputs["ift"].clear()
                self.field_values["ift"] = ""
                self.ift_was_applied = False

            self.selected_ift_treatment = treatment

        self._update_ift_reference()

    def _use_ift_reference(self) -> None:
        if not self.ift_use_button.isEnabled():
            return

        key = (self.selected_oil_id, self.selected_ift_treatment)
        ift = self.ift_references[key]

        self.field_inputs["ift"].setText(f"{ift * 1e3:.6g}")
        self.ift_was_applied = True

    def _mark_ift_manual(self, _text: str) -> None:
        self.ift_was_applied = False

    def _update_property_assistant_availability(self) -> None:
        available = self.selected_oil_id is not None

        self.property_assistant_toggle.setEnabled(available)
        self.property_assistant_arrow.setEnabled(available)

        state = "available" if available else "locked"

        self.property_assistant_status.setText("AVAILABLE" if available else "LOCKED")

        self.property_assistant_hint.setText(
            "Estimate viscosity or use laboratory IFT references."
            if available
            else "Select a registered oil to enable reference tools."
        )

        self.property_assistant_toggle.setToolTip(
            "Open reference tools" if available else "Select a registered oil first"
        )

        self.property_assistant_panel.setProperty("assistantState", state)
        self.property_assistant_status.setProperty("assistantState", state)

        # Refresh Qt styles after changing dynamic properties.
        for widget in (
            self.property_assistant_panel,
            self.property_assistant_status,
        ):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

        if not available:
            self.property_assistant_expanded = False
            self.property_assistant_content.hide()
            self.property_assistant_arrow.setText("▸")

    def _build_prediction_panel(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        margin = self._space("xl")
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(self._space("lg"))

        # Header: description on the left, action on the right.
        header = QHBoxLayout()
        header.setSpacing(self._space("lg"))

        header_text = QVBoxLayout()
        header_text.setSpacing(self._space("sm"))

        header_text.addWidget(self._label("SSDI prediction", "cardTitle"))
        header_text.addWidget(
            self._label(
                "Calculate the median droplet diameter using "
                "the selected calibration and release conditions.",
                "cardSubtitle",
                wrap=True,
            )
        )

        header.addLayout(header_text, 1)

        predict_button = QPushButton("Predict D50")
        self.predict_button = predict_button
        predict_button.setObjectName("predictD50")
        predict_button.setCheckable(False)
        predict_button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        predict_button.setCursor(Qt.CursorShape.PointingHandCursor)
        predict_button.setMinimumHeight(self._space("huge"))
        predict_button.clicked.connect(self._predict_d50)

        header.addWidget(
            predict_button,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addLayout(header)

        self.prediction_error = self._label("", "predictionError", wrap=True)
        self.prediction_error.hide()
        layout.addWidget(self.prediction_error)

        # Results container.
        self.prediction_result = QWidget()
        result_layout = QVBoxLayout(self.prediction_result)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(self._space("md"))

        # Main prediction.
        hero = QFrame()
        hero.setObjectName("predictionHero")

        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(margin, margin, margin, margin)
        hero_layout.setSpacing(self._space("sm"))

        heading = self._label(
            "PREDICTED MEDIAN DROPLET DIAMETER",
            "predictionEyebrow",
        )
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(heading)

        self.predicted_d50 = self._label("—", "predictionValue")
        self.predicted_d50.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(self.predicted_d50)

        self.prediction_physics_info = self._label("", "predictionMeta", wrap=True)
        self.prediction_physics_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(self.prediction_physics_info)

        self.prediction_model_info = self._label("", "predictionMeta", wrap=True)
        self.prediction_model_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(self.prediction_model_info)

        result_layout.addWidget(hero)

        # Dimensionless groups.
        metrics = QHBoxLayout()
        metrics.setSpacing(self._space("md"))

        def create_metric(title: str) -> tuple[QFrame, QLabel]:
            tile = QFrame()
            tile.setObjectName("predictionMetric")

            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(
                self._space("lg"),
                self._space("lg"),
                self._space("lg"),
                self._space("lg"),
            )
            tile_layout.setSpacing(self._space("sm"))

            tile_layout.addWidget(self._label(title, "predictionMetricName"))

            value = self._label("—", "predictionMetricValue")
            tile_layout.addWidget(value)

            return tile, value

        for name, attribute in (
            ("Reynolds number", "prediction_reynolds"),
            ("Weber number", "prediction_weber"),
            ("Capillary number", "prediction_capillary"),
        ):
            tile, value = create_metric(name)
            setattr(self, attribute, value)
            metrics.addWidget(tile, 1)

        result_layout.addLayout(metrics)

        # Scientific applicability warning.
        warning_frame = QFrame()
        warning_frame.setObjectName("predictionWarningFrame")

        warning_layout = QVBoxLayout(warning_frame)
        warning_layout.setContentsMargins(
            self._space("lg"),
            self._space("md"),
            self._space("lg"),
            self._space("md"),
        )
        warning_layout.setSpacing(self._space("xs"))

        self.prediction_warning_title = self._label("", "predictionWarningTitle")
        warning_layout.addWidget(self.prediction_warning_title)

        self.prediction_warning = self._label("", "predictionWarningText", wrap=True)
        warning_layout.addWidget(self.prediction_warning)

        result_layout.addWidget(warning_frame)

        self.prediction_result.hide()
        layout.addWidget(self.prediction_result)

        return card

    def _invalidate_prediction(self, *_args) -> None:
        panel = getattr(self, "prediction_result", None)

        if panel is not None and isValid(panel):
            panel.hide()

    def _build_body(self) -> QWidget:
        body = QWidget()
        body.setObjectName("body")

        layout = QVBoxLayout(body)
        margin = self._space("xxl")

        layout.setContentsMargins(margin, self._space("lg"), margin, margin)
        layout.setSpacing(0)

        model_card = QFrame()
        model_card.setObjectName("card")
        model_layout = QVBoxLayout(model_card)
        card_margin = self._space("xl")
        model_layout.setContentsMargins(
            card_margin, card_margin, card_margin, card_margin
        )
        model_layout.setSpacing(0)
        model_layout.addWidget(self._label("Calibration model", "cardTitle"))
        model_layout.addSpacing(self._space("sm"))
        model_layout.addWidget(
            self._label(
                "Select a calibrated model. No fitting or optimization is performed here.",
                "cardSubtitle",
                wrap=True,
            )
        )
        model_layout.addSpacing(self._space("xl"))
        model_layout.addWidget(self._label("MODEL VERSION", "fieldLabel"))
        model_layout.addSpacing(self._space("sm"))

        buttons = QGridLayout()
        buttons.setHorizontalSpacing(self._space("md"))
        buttons.setVerticalSpacing(self._space("md"))

        columns = 2 if self.text_scale >= 125 else 4

        for index, (version, name) in enumerate(MODEL_NAMES.items()):
            button = QPushButton(name)
            button.setObjectName("modelOption")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setMinimumHeight(self._space("huge"))
            button.setAccessibleName(f"Calibration: {name}")
            self.model_button_group.addButton(button)
            self.model_buttons[version] = button
            button.clicked.connect(
                lambda _checked=False, key=version: self.select_model(key)
            )
            buttons.addWidget(
                button,
                index // columns,
                index % columns,
            )

        for column_index in range(columns):
            buttons.setColumnStretch(column_index, 1)

        model_layout.addLayout(buttons)

        model_layout.addSpacing(self._space("sm"))

        self.model_availability_note = self._label(
            "",
            "note",
            wrap=True,
        )
        model_layout.addWidget(self.model_availability_note)

        model_layout.addSpacing(self._space("md"))
        self.model_description = self._label("", "description", wrap=True)
        model_layout.addWidget(self.model_description)
        model_layout.addSpacing(self._space("xl"))

        metrics = QHBoxLayout()
        metrics.setSpacing(self._space("lg"))
        a_card, self.a_value = self._metric("COEFFICIENT A", "Model parameter")
        b_card, self.b_value = self._metric("COEFFICIENT B", "Model parameter")
        metrics.addWidget(a_card, 1)
        metrics.addWidget(b_card, 1)
        model_layout.addLayout(metrics)

        model_layout.addSpacing(self._space("lg"))
        model_layout.addWidget(
            self._label(
                "SOURCE  ·  data/results/ssdi/predictions.xlsx  ·  Loaded once at startup",
                "note",
                wrap=True,
            )
        )

        field_card = QFrame()
        field_card.setObjectName("card")

        field_layout = QVBoxLayout(field_card)
        field_layout.setContentsMargins(
            card_margin, card_margin, card_margin, card_margin
        )
        field_layout.setSpacing(self._space("lg"))

        field_layout.addWidget(self._label("Release conditions", "cardTitle"))

        field_layout.addWidget(
            self._label(
                "Configure the release geometry and operating conditions. "
                "Initial values are illustrative.",
                "cardSubtitle",
                wrap=True,
            )
        )

        fields = [
            ("nozzle_diameter", "Nozzle diameter (mm)", "e.g. 470"),
            ("oil_flow", "Oil flow rate (m³/day)", "e.g. 12000"),
            ("gor", "Local GOR (m³/m³)", "e.g. 0.9"),
            ("gas_density", "Gas density at release (kg/m³)", "Required if GOR > 0"),
        ]

        grid = QGridLayout()
        grid.setHorizontalSpacing(self._space("xl"))
        grid.setVerticalSpacing(self._space("lg"))

        for index, (key, title, placeholder) in enumerate(fields):
            column = QVBoxLayout()
            column.setSpacing(self._space("sm"))

            column.addWidget(self._label(title, "fieldLabel"))

            editor = QLineEdit()
            editor.setObjectName("fieldInput")
            editor.setText(self.field_values.get(key, ""))
            editor.setPlaceholderText(placeholder)
            editor.setAccessibleName(title)
            editor.setMinimumHeight(self._space("huge"))

            validator = QDoubleValidator(0.0, 1e12, 8, editor)
            locale = QLocale.c()
            locale.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)

            validator.setLocale(locale)
            editor.setValidator(validator)
            editor.textChanged.connect(self._invalidate_prediction)

            if key == "ift":
                editor.textEdited.connect(self._mark_ift_manual)

            column.addWidget(editor)

            grid.addLayout(
                column,
                index // 2,
                index % 2,
            )

            self.field_inputs[key] = editor

        field_layout.addLayout(grid)

        oil_card = QFrame()
        oil_card.setObjectName("card")

        oil_layout = QVBoxLayout(oil_card)
        oil_layout.setContentsMargins(
            card_margin, card_margin, card_margin, card_margin
        )
        oil_layout.setSpacing(self._space("lg"))

        oil_header = QHBoxLayout()
        oil_header.setSpacing(self._space("md"))

        oil_header.addWidget(self._label("Oil properties", "cardTitle"))
        oil_header.addStretch()

        register_button = QPushButton("+  Register oil")
        self.register_button = register_button
        register_button.setObjectName("registerOil")
        register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        register_button.setMinimumHeight(self._space("huge"))
        register_button.setToolTip(
            "Oil registration will be available in a future version."
        )

        register_button.clicked.connect(self._show_register_notice)

        oil_header.addWidget(register_button)
        oil_layout.addLayout(oil_header)

        # Information banner, initially hidden
        self.register_banner = QFrame()
        self.register_banner.setObjectName("comingSoonBanner")

        notice_layout = QHBoxLayout(self.register_banner)
        notice_layout.setContentsMargins(
            self._space("lg"),
            self._space("md"),
            self._space("lg"),
            self._space("md"),
        )
        notice_layout.setSpacing(self._space("md"))

        notice_label = self._label(
            "Oil registration is coming soon. "
            "For now, select Custom oil to enter properties manually. "
            "Custom properties will not be saved as a registered oil.",
            "cardSubtitle",
            wrap=True,
        )

        notice_layout.addWidget(notice_label, 1)

        dismiss_button = QPushButton("×")
        dismiss_button.setObjectName("noticeDismiss")
        dismiss_button.setAccessibleName("Dismiss information")
        dismiss_button.setFixedSize(
            self._space("xxl"),
            self._space("xxl"),
        )
        dismiss_button.clicked.connect(self._dismiss_register_notice)

        notice_layout.addWidget(dismiss_button)

        self.register_banner.hide()
        oil_layout.addWidget(self.register_banner)

        oil_layout.addWidget(
            self._label(
                "Specify the oil properties at the relevant " "release conditions.",
                "cardSubtitle",
                wrap=True,
            )
        )

        oil_layout.addWidget(self._build_oil_selector())

        self.oil_reference_label = self._label(
            "",
            "cardSubtitle",
            wrap=True,
        )

        self.oil_reference_label.setText(self._oil_reference_text(self.selected_oil_id))

        oil_layout.addWidget(self.oil_reference_label)

        oil_fields = [
            ("oil_density", "Oil density (kg/m³)"),
            ("oil_viscosity", "Dynamic viscosity (mPa·s)"),
            ("ift", "Interfacial tension (mN/m)"),
        ]

        oil_grid = QGridLayout()
        oil_grid.setHorizontalSpacing(self._space("xl"))
        oil_grid.setVerticalSpacing(self._space("lg"))

        for index, (key, title) in enumerate(oil_fields):
            column = QVBoxLayout()
            column.setSpacing(self._space("sm"))

            column.addWidget(self._label(title, "fieldLabel"))

            editor = QLineEdit()
            editor.setObjectName("fieldInput")
            editor.setText(self.field_values.get(key, ""))
            editor.setAccessibleName(title)
            editor.setMinimumHeight(self._space("huge"))

            validator = QDoubleValidator(0.0, 1e12, 8, editor)

            locale = QLocale.c()
            locale.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)

            validator.setLocale(locale)
            editor.setValidator(validator)
            editor.textChanged.connect(self._invalidate_prediction)

            column.addWidget(editor)

            oil_grid.addLayout(
                column,
                0,
                index,
            )

            self.field_inputs[key] = editor

        for column_index in range(3):
            oil_grid.setColumnStretch(column_index, 1)

        oil_layout.addLayout(oil_grid)

        # Expandable property assistant.
        assistant = QFrame()
        assistant.setObjectName("propertyAssistant")
        self.property_assistant_panel = assistant

        assistant_layout = QVBoxLayout(assistant)
        assistant_layout.setContentsMargins(
            self._space("lg"),
            self._space("lg"),
            self._space("lg"),
            self._space("lg"),
        )
        assistant_layout.setSpacing(self._space("md"))

        assistant_header = QHBoxLayout()
        assistant_header.setSpacing(self._space("md"))

        assistant_icon = self._label("☷", "assistantIcon")
        assistant_header.addWidget(assistant_icon)

        assistant_text = QVBoxLayout()
        assistant_text.setSpacing(self._space("xs"))

        self.property_assistant_toggle = QPushButton("Property assistant")
        self.property_assistant_toggle.setObjectName("propertyAssistantToggle")
        self.property_assistant_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.property_assistant_toggle.setAccessibleName(
            "Collapse property assistant"
            if self.property_assistant_expanded
            else "Expand property assistant"
        )
        self.property_assistant_toggle.clicked.connect(self._toggle_property_assistant)

        assistant_text.addWidget(self.property_assistant_toggle)

        self.property_assistant_hint = self._label(
            "Optional · Estimate viscosity or use " "laboratory IFT references",
            "assistantSubtitle",
            wrap=True,
        )

        assistant_text.addWidget(self.property_assistant_hint)

        assistant_header.addLayout(assistant_text, 1)

        self.property_assistant_status = self._label(
            "",
            "assistantStatus",
        )

        assistant_header.addWidget(self.property_assistant_status)

        self.property_assistant_arrow = QPushButton(
            "▾" if self.property_assistant_expanded else "▸"
        )
        self.property_assistant_arrow.setObjectName("propertyAssistantArrow")
        self.property_assistant_arrow.setCursor(Qt.CursorShape.PointingHandCursor)
        self.property_assistant_arrow.setAccessibleName("Toggle property assistant")
        self.property_assistant_arrow.setMinimumWidth(self._space("xxl"))
        self.property_assistant_arrow.clicked.connect(self._toggle_property_assistant)

        assistant_header.addWidget(self.property_assistant_arrow)

        assistant_layout.addLayout(assistant_header)

        # Optional viscosity estimation section.
        estimation_card = QFrame()
        estimation_card.setObjectName("optionalSection")

        # Assistant content.
        estimation_card = QWidget()

        estimation_layout = QVBoxLayout(estimation_card)
        estimation_layout.setContentsMargins(0, 0, 0, 0)
        estimation_layout.setSpacing(self._space("sm"))

        estimation_layout.addWidget(
            self._label(
                "Dynamic viscosity",
                "fieldLabel",
            )
        )

        estimation_layout.addWidget(
            self._label(
                "Estimate stabilized-oil viscosity between "
                "20 and 50°C, or enter the viscosity manually.",
                "cardSubtitle",
                wrap=True,
            )
        )

        estimate_row = QHBoxLayout()
        estimate_row.setSpacing(self._space("md"))

        temperature_column = QVBoxLayout()
        temperature_column.setSpacing(self._space("sm"))

        temperature_column.addWidget(
            self._label(
                "Oil temperature (°C)",
                "fieldLabel",
            )
        )

        temperature_editor = QLineEdit()
        temperature_editor.setObjectName("fieldInput")
        temperature_editor.setPlaceholderText("e.g. 35")
        temperature_editor.setAccessibleName("Oil temperature")
        temperature_editor.setMinimumHeight(self._space("huge"))
        temperature_editor.setText(self.field_values.get("oil_temperature", ""))

        temperature_validator = QDoubleValidator(0.0, 200.0, 4, temperature_editor)
        temperature_validator.setLocale(QLocale.c())
        temperature_editor.setValidator(temperature_validator)

        temperature_editor.textChanged.connect(
            lambda value: self.field_values.__setitem__("oil_temperature", value)
        )

        self.field_inputs["oil_temperature"] = temperature_editor

        temperature_column.addWidget(temperature_editor)
        estimate_row.addLayout(temperature_column, 1)

        estimate_button = QPushButton("Estimate μ")
        estimate_button.setObjectName("viscosityEstimate")
        estimate_button.setCheckable(False)
        estimate_button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        estimate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        estimate_button.setMinimumHeight(self._space("huge"))
        estimate_button.clicked.connect(self._use_estimated_viscosity)

        estimate_row.addWidget(
            estimate_button,
            0,
            Qt.AlignmentFlag.AlignBottom,
        )

        estimation_layout.addLayout(estimate_row)

        self.viscosity_note = self._label(
            "",
            "note",
            wrap=True,
        )
        estimation_layout.addWidget(self.viscosity_note)

        # IFT assistant will be connected in the next stage.
        estimation_layout.addWidget(
            self._label(
                "Interfacial tension · Laboratory references",
                "fieldLabel",
            )
        )

        treatment_row = QHBoxLayout()
        treatment_row.setSpacing(self._space("sm"))

        treatment_group = QButtonGroup(estimation_card)
        treatment_group.setExclusive(True)

        for treatment, title in (
            ("untreated", "Untreated"),
            ("corexit", "Corexit 9500A"),
            ("finasol", "Finasol IBC"),
        ):
            button = QPushButton(title)
            button.setObjectName("iftOption")
            button.setCheckable(True)
            button.setChecked(treatment == self.selected_ift_treatment)
            button.setCursor(Qt.CursorShape.PointingHandCursor)

            treatment_group.addButton(button)

            button.clicked.connect(
                lambda checked=False, value=treatment: self._select_ift_treatment(value)
            )

            treatment_row.addWidget(button, 1)

        estimation_layout.addLayout(treatment_row)

        self.ift_preview = self._label(
            "",
            "note",
            wrap=True,
        )
        estimation_layout.addWidget(self.ift_preview)

        self.ift_use_button = QPushButton("Use reference")
        self.ift_use_button.setObjectName("iftUseReference")
        self.ift_use_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ift_use_button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.ift_use_button.clicked.connect(self._use_ift_reference)

        estimation_layout.addWidget(
            self.ift_use_button,
            0,
            Qt.AlignmentFlag.AlignLeft,
        )

        self._update_ift_reference()

        self.property_assistant_content = estimation_card

        assistant_layout.addWidget(estimation_card)

        estimation_card.setVisible(self.property_assistant_expanded)

        oil_layout.addWidget(assistant)

        self._update_property_assistant_availability()

        layout.addWidget(oil_card)

        layout.addSpacing(self._space("lg"))
        layout.addWidget(model_card)

        layout.addSpacing(self._space("lg"))
        layout.addWidget(field_card)

        layout.addSpacing(self._space("lg"))
        layout.addWidget(self._build_prediction_panel())

        layout.addStretch()
        return body

    def select_model(self, version: str) -> None:
        if version == "jax_oil_wise":
            if self.selected_oil_id not in self.oil_wise_calibrations:
                return
        elif version not in self.calibrations:
            raise ValueError(f"Calibration not loaded: {version}")

        self.selected_model = version
        self.model_buttons[version].setChecked(True)
        self.update_coefficients()
        self._invalidate_prediction()

    def _scroll_to_prediction(self) -> None:
        result_widget = getattr(self, "prediction_result", None)

        if (
            result_widget is None
            or not isValid(result_widget)
            or not result_widget.isVisible()
        ):
            return

        content = self.content_scroll.widget()
        if content is None:
            return

        scrollbar = self.content_scroll.verticalScrollBar()
        viewport_height = self.content_scroll.viewport().height()

        top = result_widget.mapTo(content, QPoint(0, 0)).y()

        bottom = top + result_widget.height()
        current = scrollbar.value()
        margin = self._space("lg")

        # Avoid moving the page if the result is fully visible.
        if top >= current + margin and bottom <= current + viewport_height - margin:
            return

        self._animate_oil_scroll(top - margin)

    def _read_prediction_scenario(self) -> dict[str, float]:
        def read(
            key: str,
            label: str,
            allow_zero: bool = False,
        ) -> float:
            text = self.field_inputs[key].text().strip()

            try:
                value = float(text)
            except ValueError:
                raise ValueError(f"Enter a valid value for {label}.") from None

            if not np.isfinite(value):
                raise ValueError(f"{label} must be finite.")

            if value < 0 or (value == 0 and not allow_zero):
                raise ValueError(f"{label} must be positive.")

            return value

        diameter_mm = read("nozzle_diameter", "nozzle diameter")
        oil_flow_day = read("oil_flow", "oil flow rate")
        gor = read("gor", "local GOR", allow_zero=True)

        oil_density = read("oil_density", "oil density")
        oil_viscosity_mpas = read("oil_viscosity", "dynamic viscosity")
        ift_mnm = read("ift", "interfacial tension")

        gas_density = read("gas_density", "gas density") if gor > 0 else 0.0

        oil_flow = oil_flow_day / 86400.0

        return {
            "nozzle_diameter": diameter_mm * 1e-3,
            "oil_flow": oil_flow,
            "gas_flow": gor * oil_flow,
            "oil_density": oil_density,
            "gas_density": gas_density,
            "oil_viscosity": oil_viscosity_mpas * 1e-3,
            "ift": ift_mnm * 1e-3,
        }

    @staticmethod
    def _format_prediction_metric(value: float) -> str:
        if value == 0 or 0.01 <= abs(value) < 10000:
            return f"{value:.3g}"

        mantissa, exponent = f"{value:.2e}".split("e")

        superscripts = str.maketrans(
            "0123456789-",
            "⁰¹²³⁴⁵⁶⁷⁸⁹⁻",
        )

        exponent_text = str(int(exponent)).translate(superscripts)

        return f"{mantissa} × 10{exponent_text}"

    def _on_prediction_failed(self, message: str) -> None:
        self.prediction_error.setText(message)
        self.prediction_error.show()

    def _on_prediction_finished(self) -> None:
        self.predict_button.setEnabled(True)
        self.predict_button.setText("Predict D50")
        self._prediction_worker = None

    def _predict_d50(self) -> None:
        if self._prediction_worker is not None:
            return

        self.prediction_error.hide()
        self.prediction_result.hide()

        try:
            scenario = self._read_prediction_scenario()

            if self.selected_model == "jax_oil_wise":
                coefficients = self.oil_wise_calibrations.get(self.selected_oil_id)

                if coefficients is None:
                    raise ValueError("Select an oil with an Oil-wise calibration.")
            else:
                coefficients = self.calibrations[self.selected_model]

            a, b = coefficients

            self._prediction_context = (
                scenario,
                a,
                b,
                self.selected_model,
            )

            worker = PredictionWorker(scenario, a, b, self)
            self._prediction_worker = worker

            worker.completed.connect(self._on_prediction_completed)
            worker.failed.connect(self._on_prediction_failed)
            worker.finished.connect(self._on_prediction_finished)
            worker.finished.connect(worker.deleteLater)

            self.predict_button.setEnabled(False)
            self.predict_button.setText("Calculating…")

            worker.start()

        except (ValueError, KeyError) as error:
            self.prediction_error.setText(str(error))
            self.prediction_error.show()

    def _on_prediction_completed(self, result: dict[str, float]) -> None:
        scenario, a, b, version = self._prediction_context

        d50_mm = result["d50_m"] * 1e3

        self.predicted_d50.setText(f"{d50_mm:.4f} mm")

        self.prediction_physics_info.setText(
            f"D50 / nozzle diameter = {result['d50_over_d']:.5g}"
        )

        self.prediction_model_info.setText(
            f"Calibration: {MODEL_NAMES[version]}  ·  " f"A = {a:.6f}  ·  B = {b:.6f}"
        )

        self.prediction_reynolds.setText(
            self._format_prediction_metric(result["reynolds"])
        )
        self.prediction_weber.setText(self._format_prediction_metric(result["weber"]))
        self.prediction_capillary.setText(
            self._format_prediction_metric(result["capillary"])
        )

        diameter_mm = scenario["nozzle_diameter"] * 1e3

        if not 2.0 <= diameter_mm <= 3.0:
            self.prediction_warning_title.setText("Outside laboratory nozzle range")
            self.prediction_warning.setText(
                f"The selected nozzle diameter ({diameter_mm:g} mm) "
                "is outside the 2–3 mm laboratory range. "
                "This prediction is an extrapolation and has "
                "not been validated for field-scale conditions."
            )
        else:
            self.prediction_warning_title.setText("Laboratory-domain validation")
            self.prediction_warning.setText(
                "The nozzle diameter is within the laboratory "
                "range of 2–3 mm. Other operating conditions "
                "may still be outside the calibration domain."
            )

        self.prediction_result.show()

        QTimer.singleShot(
            0,
            self._scroll_to_prediction,
        )

    def update_coefficients(self) -> None:
        if self.selected_model == "jax_oil_wise":
            a, b = self.oil_wise_calibrations[self.selected_oil_id]

            description = (
                f"Oil-wise calibration for "
                f"{self.oil_labels[self.selected_oil_id]}. "
                "Fitted to laboratory data for this oil; "
                "field-scale validity is not established."
            )
        else:
            a, b = self.calibrations[self.selected_model]

            description = MODEL_DESCRIPTIONS.get(self.selected_model, "")

        self.a_value.setText(f"{a:.6f}")
        self.b_value.setText(f"{b:.6f}")
        self.model_description.setText(description)

    def change_text_scale(self, scale: int) -> None:
        if scale not in TEXT_SCALES:
            raise ValueError(f"Unsupported text scale: {scale}")
        if scale == self.text_scale:
            return
        self.text_scale = scale
        self.settings.setValue("accessibility/text_scale", scale)
        self.settings.sync()
        self._render()


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    predictions_path = Path("data/results/ssdi/predictions.xlsx")
    calibrations = load_global_calibrations(predictions_path)
    oil_wise_calibrations = load_oil_wise_calibrations(
        predictions_path,
        paths.EXPERIMENTS_DATABASE,
    )

    oils = load_oil_properties()

    ift_references = load_ift_references()

    window = SSDIWindow(
        calibrations,
        oils,
        ift_references,
        oil_wise_calibrations,
    )
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
