
# ============================================================
# FjBa | BASIC SCALE GRID GENERATOR FOR QGIS
# Version 1.1 | Basic Edition
#
# FjBa metallic emerald / gold branding
# with animated light sweep.
#
# Compatible with QGIS 3.x / Python 3 / PyQt5
#
# BASIC FEATURES
# - A0 to A4 paper formats
# - Portrait / Landscape
# - Scale-based dimensions
# - Rectangle / Square
# - Projected CRS support
# - Basic frame styling
# - Grid labels
# - Automatic numbering
# - Grid manager
# - Rename / Delete
# - Save / Load JSON configurations
# - Click-to-place workflow
#
# PRO-ONLY FEATURES ARE NOT INCLUDED.
# ============================================================

import json
import traceback

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QMessageBox,
    QRadioButton, QCheckBox, QTreeWidget,
    QTreeWidgetItem, QAbstractItemView,
    QDoubleSpinBox, QLineEdit, QFileDialog,
    QGroupBox, QFormLayout, QFrame, QApplication
)

from qgis.PyQt.QtCore import (
    Qt, QVariant, QDateTime, QTimer
)

from qgis.PyQt.QtGui import (
    QColor, QFont, QPainter, QPainterPath,
    QLinearGradient, QPen, QBrush
)

from qgis.gui import QgsMapTool, QgsRubberBand

from qgis.core import (
    Qgis,
    QgsProject, QgsVectorLayer, QgsFeature,
    QgsGeometry, QgsPointXY, QgsField,
    QgsFillSymbol, QgsSingleSymbolRenderer,
    QgsUnitTypes, QgsPalLayerSettings,
    QgsTextFormat, QgsVectorLayerSimpleLabeling,
    QgsWkbTypes
)


# ============================================================
# ANIMATED FjBa METALLIC LOGO
# Gold / Emerald gradient with animated light sweep
# ============================================================

class FjBaMetallicLogo(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.phase = 0.0

        self.setMinimumSize(70, 70)
        self.setMaximumSize(90, 90)

        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_animation)
        self.timer.start(35)

    def advance_animation(self):

        self.phase = (self.phase + 0.018) % 1.5
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        font = QFont("Segoe UI", 27, QFont.Bold)
        painter.setFont(font)

        text = "FjBa"
        metrics = painter.fontMetrics()

        text_width = metrics.horizontalAdvance(text)
        x = (rect.width() - text_width) / 2
        baseline = rect.height() * 0.62

        path = QPainterPath()
        path.addText(x, baseline, font, text)

        # Metallic emerald and gold lettering
        gradient = QLinearGradient(
            0, 0,
            rect.width(), rect.height()
        )

        gradient.setColorAt(0.0, QColor("#FFF2B0"))
        gradient.setColorAt(0.22, QColor("#D5A832"))
        gradient.setColorAt(0.45, QColor("#F9E7A0"))
        gradient.setColorAt(0.68, QColor("#16A879"))
        gradient.setColorAt(1.0, QColor("#075C43"))

        painter.setPen(
            QPen(QColor("#B68A28"), 0.8)
        )

        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

        # Animated white light sweep
        sweep_x = self.phase * rect.width()

        sweep = QLinearGradient(
            sweep_x - 12, 0,
            sweep_x + 12, 0
        )

        sweep.setColorAt(
            0.0, QColor(255, 255, 255, 0)
        )

        sweep.setColorAt(
            0.5, QColor(255, 255, 255, 180)
        )

        sweep.setColorAt(
            1.0, QColor(255, 255, 255, 0)
        )

        painter.save()
        painter.setClipPath(path)
        painter.fillRect(rect, sweep)
        painter.restore()

        painter.end()

    def stop(self):

        if self.timer.isActive():
            self.timer.stop()


# ============================================================
# PAPER DATABASE
# ============================================================

PAPER_FORMATS = {
    "A4": (210, 297),
    "A3": (297, 420),
    "A2": (420, 594),
    "A1": (594, 841),
    "A0": (841, 1189)
}


# ============================================================
# FRAME COLOURS
# ============================================================

FRAME_COLORS = {
    "Blue": "0,120,255",
    "Red": "255,0,0",
    "Black": "0,0,0",
    "Orange": "255,120,0",
    "Green": "0,180,0"
}


# ============================================================
# MAP PLACEMENT TOOL
# ============================================================

# ============================================================
# MAP PLACEMENT TOOL WITH REAL-TIME GRID PREVIEW
# ============================================================

class BasicGridPlacementTool(QgsMapTool):

    def __init__(self, canvas, parent):

        super().__init__(canvas)

        self.canvas = canvas
        self.parent = parent

        # Live preview rubber band
        self.preview = QgsRubberBand(
            self.canvas,
            QgsWkbTypes.PolygonGeometry
        )

        self.preview.setColor(
            QColor(0, 220, 180, 220)
        )

        self.preview.setFillColor(
            QColor(0, 220, 180, 35)
        )

        self.preview.setWidth(2)

        self.preview.setLineStyle(
            Qt.DashLine
        )

        self.preview.setVisible(False)

    # --------------------------------------------------------
    # CREATE PREVIEW GEOMETRY
    # --------------------------------------------------------

    def create_preview_geometry(self, x, y):

        width = self.parent.grid_width
        height = self.parent.grid_height

        xmin = x - width / 2
        xmax = x + width / 2

        ymin = y - height / 2
        ymax = y + height / 2

        polygon = [
            QgsPointXY(xmin, ymin),
            QgsPointXY(xmax, ymin),
            QgsPointXY(xmax, ymax),
            QgsPointXY(xmin, ymax),
            QgsPointXY(xmin, ymin)
        ]

        return QgsGeometry.fromPolygonXY([
            polygon
        ])

    # --------------------------------------------------------
    # REAL-TIME MOUSE MOVEMENT
    # --------------------------------------------------------

    def canvasMoveEvent(self, event):

        if (
            self.parent.grid_width <= 0
            or self.parent.grid_height <= 0
        ):
            return

        point = self.toMapCoordinates(
            event.pos()
        )

        geometry = self.create_preview_geometry(
            point.x(),
            point.y()
        )

        self.preview.setToGeometry(
            geometry,
            self.parent.layer
        )

        self.preview.setVisible(True)

    # --------------------------------------------------------
    # LEFT CLICK = PLACE GRID
    # RIGHT CLICK = STOP
    # --------------------------------------------------------

    def canvasReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:

            point = self.toMapCoordinates(
                event.pos()
            )

            self.parent.create_grid(
                point.x(),
                point.y()
            )

            # Clear preview until the next mouse movement
            self.preview.reset()

            self.preview.setVisible(False)

        elif event.button() == Qt.RightButton:

            self.preview.reset()

            self.preview.setVisible(False)

            self.canvas.unsetMapTool(self)

            self.parent.map_tool = None

            self.parent.status.setText(
                "Placement stopped"
            )

    # --------------------------------------------------------
    # CLEAN UP WHEN TOOL IS DEACTIVATED
    # --------------------------------------------------------

    def deactivate(self):

        self.preview.reset()

        self.preview.setVisible(False)

        super().deactivate()


# ============================================================
# MAIN WINDOW
# ============================================================

class FjBaBasicGridGenerator(QWidget):

    def __init__(self, iface):

        super().__init__()

        self.iface = iface
        self.canvas = iface.mapCanvas()

        self.layer = None
        self.counter = 1
        self.current_scale = 500

        self.grid_width = 0
        self.grid_height = 0

        self.orientation = "Landscape"
        self.map_tool = None

        # Logo reference is initialized before the interface
        self.logo = None

        self.setWindowTitle(
            "FjBa | Basic Scale Grid Generator"
        )

        # Safely obtain screen dimensions
        screen = self.screen()

        if screen is None:
            screen = QApplication.primaryScreen()

        if screen is not None:

            available = screen.availableGeometry()

            window_width = min(
                1100,
                available.width() - 80
            )

            window_height = min(
                900,
                available.height() - 100
            )

            self.resize(
                max(850, window_width),
                max(650, window_height)
            )

        else:

            self.resize(1000, 850)

        self.setMinimumSize(850, 650)

        # Build interface
        self.create_interface()

        self.apply_theme()
        self.connect_signals()

    # ========================================================
    # INTERFACE
    # ========================================================

    def create_interface(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(
            18, 18, 18, 18
        )

        root.setSpacing(12)

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = QFrame()

        header.setObjectName(
            "FjBaHeader"
        )

        header_layout = QHBoxLayout(header)

        header_layout.setContentsMargins(
            14, 8, 18, 8
        )

        # Create the embedded metallic logo
        self.logo = FjBaMetallicLogo()

        heading_layout = QVBoxLayout()

        eyebrow = QLabel(
            "FjBa  /  QGIS TOOLKIT"
        )

        eyebrow.setObjectName(
            "FjBaEyebrow"
        )

        heading = QLabel(
            "Basic Scale Grid Generator"
        )

        heading.setObjectName(
            "FjBaHeading"
        )

        subtitle = QLabel(
            "Simple and reliable map frame creation"
        )

        subtitle.setObjectName(
            "FjBaSubtitle"
        )

        heading_layout.addWidget(eyebrow)
        heading_layout.addWidget(heading)
        heading_layout.addWidget(subtitle)

        header_layout.addWidget(self.logo)

        header_layout.addLayout(
            heading_layout,
            1
        )

        root.addWidget(header)

        # ----------------------------------------------------
        # MAIN CONTENT
        # ----------------------------------------------------

        content = QHBoxLayout()

        content.setSpacing(12)

        root.addLayout(
            content,
            1
        )

        # ----------------------------------------------------
        # LEFT: SETTINGS
        # ----------------------------------------------------

        settings_group = QGroupBox(
            "Grid settings"
        )

        settings_layout = QVBoxLayout(
            settings_group
        )

        # PAPER

        paper_group = QGroupBox(
            "01  ·  Paper"
        )

        paper_form = QFormLayout(
            paper_group
        )

        self.paper_box = QComboBox()

        self.paper_box.addItems(
            list(PAPER_FORMATS.keys())
        )

        paper_form.addRow(
            "Paper format",
            self.paper_box
        )

        orientation_row = QHBoxLayout()

        self.landscape = QRadioButton(
            "Landscape"
        )

        self.portrait = QRadioButton(
            "Portrait"
        )

        self.landscape.setChecked(True)

        orientation_row.addWidget(
            self.landscape
        )

        orientation_row.addWidget(
            self.portrait
        )

        paper_form.addRow(
            "Orientation",
            orientation_row
        )

        settings_layout.addWidget(
            paper_group
        )

        # SCALE

        scale_group = QGroupBox(
            "02  ·  Scale"
        )

        scale_form = QFormLayout(
            scale_group
        )

        self.scale_input = QLineEdit("500")

        scale_form.addRow(
            "Scale 1 :",
            self.scale_input
        )

        self.margin_input = QLineEdit("5")

        scale_form.addRow(
            "Page margin (mm)",
            self.margin_input
        )

        shape_row = QHBoxLayout()

        self.rectangle = QRadioButton(
            "Rectangle"
        )

        self.square = QRadioButton(
            "Square"
        )

        self.rectangle.setChecked(True)

        shape_row.addWidget(
            self.rectangle
        )

        shape_row.addWidget(
            self.square
        )

        scale_form.addRow(
            "Grid shape",
            shape_row
        )

        settings_layout.addWidget(
            scale_group
        )

        # FRAME STYLE

        style_group = QGroupBox(
            "03  ·  Frame appearance"
        )

        style_form = QFormLayout(
            style_group
        )

        self.outline_color = QComboBox()

        self.outline_color.addItems(
            list(FRAME_COLORS.keys())
        )

        self.outline_width = QDoubleSpinBox()

        self.outline_width.setRange(
            0.1,
            10
        )

        self.outline_width.setValue(1.0)
        self.outline_width.setSingleStep(0.1)

        self.fill_transparency = QDoubleSpinBox()

        self.fill_transparency.setRange(
            0,
            100
        )

        self.fill_transparency.setValue(10)

        style_form.addRow(
            "Outline colour",
            self.outline_color
        )

        style_form.addRow(
            "Outline width",
            self.outline_width
        )

        style_form.addRow(
            "Fill transparency (%)",
            self.fill_transparency
        )

        settings_layout.addWidget(
            style_group
        )

        # DISPLAY

        display_group = QGroupBox(
            "04  ·  Display"
        )

        display_layout = QVBoxLayout(
            display_group
        )

        self.show_labels = QCheckBox(
            "Show grid labels"
        )

        self.show_labels.setChecked(True)

        self.numbering = QCheckBox(
            "Automatic numbering"
        )

        self.numbering.setChecked(True)

        display_layout.addWidget(
            self.show_labels
        )

        display_layout.addWidget(
            self.numbering
        )

        settings_layout.addWidget(
            display_group
        )

        # START BUTTON

        self.start_button = QPushButton(
            "▶   Start placement"
        )

        self.start_button.setObjectName(
            "FjBaPrimary"
        )

        self.start_button.setMinimumHeight(
            45
        )

        settings_layout.addWidget(
            self.start_button
        )

        settings_layout.addStretch(1)

        content.addWidget(
            settings_group,
            1
        )

        # ----------------------------------------------------
        # RIGHT: GRID MANAGER
        # ----------------------------------------------------

        manager_group = QGroupBox(
            "Grid manager"
        )

        manager_layout = QVBoxLayout(
            manager_group
        )

        description = QLabel(
            "Manage the grid frames created in your project."
        )

        manager_layout.addWidget(
            description
        )

        self.grid_tree = QTreeWidget()

        self.grid_tree.setHeaderLabels([
            "ID",
            "Name",
            "Scale",
            "Format",
            "Orientation"
        ])

        self.grid_tree.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.grid_tree.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.grid_tree.setAlternatingRowColors(
            True
        )

        self.grid_tree.setRootIsDecorated(
            False
        )

        manager_layout.addWidget(
            self.grid_tree,
            1
        )

        self.delete_button = QPushButton(
            "Delete selected grid"
        )

        self.delete_button.setObjectName(
            "FjBaDanger"
        )

        self.save_button = QPushButton(
            "Save configuration"
        )

        self.load_button = QPushButton(
            "Load configuration"
        )

        manager_layout.addWidget(
            self.delete_button
        )

        manager_layout.addWidget(
            self.save_button
        )

        manager_layout.addWidget(
            self.load_button
        )

        content.addWidget(
            manager_group,
            1
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status = QLabel(
            "Ready  ·  Configure your grid and start placement"
        )

        self.status.setObjectName(
            "FjBaStatus"
        )

        root.addWidget(
            self.status
        )

    # ========================================================
    # THEME
    # ========================================================

    def apply_theme(self):

        self.setStyleSheet("""
            QWidget {
                background: #0B1220;
                color: #E7EEF8;
                font-family: "Segoe UI", Arial;
                font-size: 10pt;
            }

            QFrame#FjBaHeader {
                background: #111F31;
                border: 1px solid #2A435B;
                border-radius: 14px;
            }

            QLabel#FjBaEyebrow {
                color: #64D6C5;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QLabel#FjBaHeading {
                color: #F4F8FC;
                font-size: 19pt;
                font-weight: bold;
            }

            QLabel#FjBaSubtitle {
                color: #93A8BF;
            }

            QLabel#FjBaStatus {
                background: #101D2E;
                border: 1px solid #263B52;
                border-radius: 8px;
                padding: 10px;
                color: #75DCCB;
                font-weight: bold;
            }

            QGroupBox {
                background: #101B2B;
                border: 1px solid #263B52;
                border-radius: 10px;
                margin-top: 12px;
                padding: 12px;
                font-weight: bold;
                color: #78D9CD;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }

            QLineEdit, QComboBox, QDoubleSpinBox {
                background: #0B1422;
                color: #F0F5FB;
                border: 1px solid #344B65;
                border-radius: 6px;
                padding: 7px;
                min-height: 20px;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QDoubleSpinBox:focus {
                border: 1px solid #55CDBD;
            }

            QPushButton {
                background: #173A4B;
                color: white;
                border: 1px solid #2D6874;
                border-radius: 7px;
                padding: 9px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #20566A;
                border-color: #56CDBD;
            }

            QPushButton#FjBaPrimary {
                background: #1B8B83;
                border: 1px solid #45BDB0;
            }

            QPushButton#FjBaPrimary:hover {
                background: #22A398;
            }

            QPushButton#FjBaDanger {
                background: #4A2935;
                border-color: #814454;
            }

            QTreeWidget {
                background: #0B1422;
                alternate-background-color: #101D2E;
                border: 1px solid #2B4058;
                border-radius: 8px;
                selection-background-color: #175E68;
            }

            QTreeWidget::item {
                padding: 6px;
            }

            QHeaderView::section {
                background: #17283B;
                color: #8FE1D5;
                padding: 8px;
                border: none;
                font-weight: bold;
            }

            QCheckBox, QRadioButton {
                spacing: 7px;
            }
        """)

    # ========================================================
    # SIGNALS
    # ========================================================

    def connect_signals(self):

        self.start_button.clicked.connect(
            self.start
        )

        self.delete_button.clicked.connect(
            self.delete_grid
        )

        self.save_button.clicked.connect(
            self.save_configuration
        )

        self.load_button.clicked.connect(
            self.load_configuration
        )

        self.outline_color.currentIndexChanged.connect(
            self.update_frame_style
        )

        self.outline_width.valueChanged.connect(
            self.update_frame_style
        )

        self.fill_transparency.valueChanged.connect(
            self.update_frame_style
        )

        self.show_labels.stateChanged.connect(
            self.toggle_labels
        )

        self.grid_tree.itemChanged.connect(
            self.rename_grid
        )

        self.grid_tree.itemSelectionChanged.connect(
            self.highlight_selected_grid
        )

    # ========================================================
    # CRS UNIT CONVERSION
    # ========================================================

    def convert_map_units(self, metres):

        units = QgsProject.instance().crs().mapUnits()

        if units == QgsUnitTypes.DistanceMeters:
            return metres

        if units == QgsUnitTypes.DistanceFeet:
            return metres * 3.280839895

        if units == QgsUnitTypes.DistanceUSSurveyFeet:
            return metres * 3.280833333

        if units == QgsUnitTypes.DistanceKilometers:
            return metres / 1000.0

        raise ValueError(
            "Unsupported CRS units. Use a projected CRS "
            "with metres, kilometres or feet."
        )

    # ========================================================
    # START PLACEMENT
    # ========================================================

    def start(self):

        try:

            scale = int(
                self.scale_input.text()
            )

            if scale <= 0:
                raise ValueError(
                    "Scale must be positive."
                )

            margin = float(
                self.margin_input.text()
            )

            if margin < 0:
                raise ValueError(
                    "Margin cannot be negative."
                )

            paper_width, paper_height = PAPER_FORMATS[
                self.paper_box.currentText()
            ]

            if self.landscape.isChecked():

                paper_width, paper_height = (
                    max(paper_width, paper_height),
                    min(paper_width, paper_height)
                )

                self.orientation = "Landscape"

            else:

                paper_width, paper_height = (
                    min(paper_width, paper_height),
                    max(paper_width, paper_height)
                )

                self.orientation = "Portrait"

            usable_width = (
                paper_width - margin * 2
            )

            usable_height = (
                paper_height - margin * 2
            )

            if usable_width <= 0 or usable_height <= 0:

                raise ValueError(
                    "Margins leave no usable paper area."
                )

            width_metres = (
                usable_width * scale / 1000.0
            )

            height_metres = (
                usable_height * scale / 1000.0
            )

            self.grid_width = self.convert_map_units(
                width_metres
            )

            self.grid_height = self.convert_map_units(
                height_metres
            )

            if self.square.isChecked():

                size = max(
                    self.grid_width,
                    self.grid_height
                )

                self.grid_width = size
                self.grid_height = size

            self.current_scale = scale

            if self.layer is None:
                self.create_layer()

            # Stop any previous placement tool
            if self.map_tool is not None:
                self.canvas.unsetMapTool(self.map_tool)

            self.map_tool = BasicGridPlacementTool(
                self.canvas,
                self
            )

            self.canvas.setMapTool(
                self.map_tool
            )
            self.canvas.refresh()

            self.status.setText(
                "Click on the map to place grid frames. "
                "Right-click to stop."
            )

        except Exception as error:

            QMessageBox.warning(
                self,
                "Grid configuration",
                str(error)
            )

    # ========================================================
    # CREATE OUTPUT LAYER
    # ========================================================

    def create_layer(self):

        crs = QgsProject.instance().crs()

        self.layer = QgsVectorLayer(
            "Polygon?crs=" + crs.authid(),
            "FjBa Basic Grid Frames",
            "memory"
        )

        if not self.layer.isValid():

            raise RuntimeError(
                "Could not create the grid layer."
            )

        provider = self.layer.dataProvider()

        provider.addAttributes([
            QgsField("ID", QVariant.Int),
            QgsField("NAME", QVariant.String),
            QgsField("SCALE", QVariant.Int),
            QgsField("FORMAT", QVariant.String),
            QgsField("ORIENT", QVariant.String),
            QgsField("WIDTH", QVariant.Double),
            QgsField("HEIGHT", QVariant.Double),
            QgsField("DATE", QVariant.String)
        ])

        self.layer.updateFields()

        QgsProject.instance().addMapLayer(
            self.layer
        )

        self.update_frame_style()
        self.update_label_settings()

    # ========================================================
    # FRAME STYLE
    # ========================================================

    def update_frame_style(self, *args):

        if self.layer is None:
            return

        outline = FRAME_COLORS[
            self.outline_color.currentText()
        ]

        alpha = int(
            255 * (
                100 - self.fill_transparency.value()
            ) / 100
        )

        symbol = QgsFillSymbol.createSimple({
            "color": f"255,255,0,{alpha}",
            "outline_color": outline,
            "outline_width": str(
                self.outline_width.value()
            )
        })

        self.layer.setRenderer(
            QgsSingleSymbolRenderer(symbol)
        )

        self.layer.triggerRepaint()
        self.canvas.refresh()

    # ========================================================
    # LABEL SETTINGS
    # ========================================================

    def update_label_settings(self):

        if self.layer is None:
            return

        settings = QgsPalLayerSettings()

        settings.fieldName = "NAME"

        settings.placement = (
            QgsPalLayerSettings.OverPoint
        )

        text_format = QgsTextFormat()

        font = QFont()
        font.setBold(True)

        text_format.setFont(font)
        text_format.setSize(10)

        settings.setFormat(text_format)

        self.layer.setLabeling(
            QgsVectorLayerSimpleLabeling(settings)
        )

        self.layer.setLabelsEnabled(
            self.show_labels.isChecked()
        )

        self.layer.triggerRepaint()

    def toggle_labels(self, *args):

        if self.layer is None:
            return

        self.layer.setLabelsEnabled(
            self.show_labels.isChecked()
        )

        self.layer.triggerRepaint()

    # ========================================================
    # CREATE GRID
    # ========================================================

    def create_grid(self, x, y):

        if self.layer is None:
            return

        width = self.grid_width
        height = self.grid_height

        xmin = x - width / 2
        xmax = x + width / 2

        ymin = y - height / 2
        ymax = y + height / 2

        polygon = [
            QgsPointXY(xmin, ymin),
            QgsPointXY(xmax, ymin),
            QgsPointXY(xmax, ymax),
            QgsPointXY(xmin, ymax),
            QgsPointXY(xmin, ymin)
        ]

        geometry = QgsGeometry.fromPolygonXY([
            polygon
        ])

        if self.numbering.isChecked():

            grid_id = self.counter
            self.counter += 1

        else:

            grid_id = 0

        name = f"Grid_{grid_id}"

        feature = QgsFeature(
            self.layer.fields()
        )

        feature.setGeometry(geometry)

        feature.setAttributes([
            grid_id,
            name,
            self.current_scale,
            self.paper_box.currentText(),
            self.orientation,
            round(width, 3),
            round(height, 3),
            QDateTime.currentDateTime().toString(
                "yyyy-MM-dd HH:mm:ss"
            )
        ])

        success = self.layer.dataProvider().addFeature(
            feature
        )

        if not success:

            QMessageBox.warning(
                self,
                "Grid creation",
                "Could not add the grid feature."
            )

            return

        self.layer.updateExtents()
        self.layer.triggerRepaint()

        # Retrieve stored feature for the manager
        stored_feature = None

        for candidate in self.layer.getFeatures():

            if (
                candidate["ID"] == grid_id
                and candidate["NAME"] == name
            ):

                stored_feature = candidate
                break

        if stored_feature is not None:
            self.add_manager_item(stored_feature)

        self.status.setText(
            f"{name} created"
        )

        self.canvas.refresh()

    # ========================================================
    # GRID MANAGER
    # ========================================================

    def add_manager_item(self, feature):

        item = QTreeWidgetItem([
            str(feature["ID"]),
            str(feature["NAME"]),
            f"1:{feature['SCALE']}",
            str(feature["FORMAT"]),
            str(feature["ORIENT"])
        ])

        item.setData(
            0,
            Qt.UserRole,
            feature.id()
        )

        item.setFlags(
            item.flags() | Qt.ItemIsEditable
        )

        self.grid_tree.blockSignals(True)

        self.grid_tree.addTopLevelItem(
            item
        )

        self.grid_tree.blockSignals(False)

    def highlight_selected_grid(self):

        if self.layer is None:
            return

        item = self.grid_tree.currentItem()

        self.layer.removeSelection()

        if item is not None:

            feature_id = item.data(
                0,
                Qt.UserRole
            )

            if feature_id is not None:
                self.layer.select(feature_id)

        self.canvas.refresh()

    # ========================================================
    # RENAME GRID
    # ========================================================

    def rename_grid(self, item, column):

        if column != 1 or self.layer is None:
            return

        feature_id = item.data(
            0,
            Qt.UserRole
        )

        if feature_id is None:
            return

        name = item.text(1).strip()

        if not name:
            return

        field_index = self.layer.fields().indexOf(
            "NAME"
        )

        success = self.layer.dataProvider().changeAttributeValues({
            feature_id: {
                field_index: name
            }
        })

        if not success:

            QMessageBox.warning(
                self,
                "Rename",
                "Could not rename this grid."
            )

        self.layer.triggerRepaint()

    # ========================================================
    # DELETE GRID
    # ========================================================

    def delete_grid(self):

        if self.layer is None:
            return

        item = self.grid_tree.currentItem()

        if item is None:

            QMessageBox.information(
                self,
                "Delete grid",
                "Select a grid first."
            )

            return

        answer = QMessageBox.question(
            self,
            "Delete grid",
            "Delete the selected grid?"
        )

        if answer != QMessageBox.Yes:
            return

        feature_id = item.data(
            0,
            Qt.UserRole
        )

        success = self.layer.dataProvider().deleteFeatures([
            feature_id
        ])

        if success:

            index = self.grid_tree.indexOfTopLevelItem(
                item
            )

            self.grid_tree.takeTopLevelItem(
                index
            )

            self.layer.updateExtents()
            self.layer.triggerRepaint()
            self.canvas.refresh()

            self.status.setText(
                "Grid deleted"
            )

        else:

            QMessageBox.warning(
                self,
                "Delete grid",
                "Could not delete the selected grid."
            )

    # ========================================================
    # SAVE CONFIGURATION
    # ========================================================

    def save_configuration(self):

        if self.layer is None:

            QMessageBox.information(
                self,
                "Save configuration",
                "There are no grids to save."
            )

            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save FjBa Basic Configuration",
            "",
            "FjBa Grid Configuration (*.json)"
        )

        if not filename:
            return

        if not filename.lower().endswith(".json"):
            filename += ".json"

        data = []

        for feature in self.layer.getFeatures():

            data.append({
                "id": feature["ID"],
                "name": feature["NAME"],
                "scale": feature["SCALE"],
                "format": feature["FORMAT"],
                "orientation": feature["ORIENT"],
                "geometry": feature.geometry().asWkt()
            })

        try:

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4
                )

            self.status.setText(
                "Configuration saved"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save error",
                str(error)
            )

    # ========================================================
    # LOAD CONFIGURATION
    # ========================================================

    def load_configuration(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load FjBa Basic Configuration",
            "",
            "FjBa Grid Configuration (*.json)"
        )

        if not filename:
            return

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if not isinstance(data, list):

                raise ValueError(
                    "The configuration must contain "
                    "a list of grids."
                )

            if self.layer is None:
                self.create_layer()

            provider = self.layer.dataProvider()

            loaded_count = 0

            for record in data:

                geometry = QgsGeometry.fromWkt(
                    record["geometry"]
                )

                if geometry.isNull() or geometry.isEmpty():
                    continue

                feature = QgsFeature(
                    self.layer.fields()
                )

                feature.setGeometry(geometry)

                feature.setAttributes([
                    int(record.get("id", 0)),
                    str(record.get("name", "Grid")),
                    int(record.get("scale", 500)),
                    str(record.get("format", "A4")),
                    str(record.get("orientation", "Landscape")),
                    0.0,
                    0.0,
                    QDateTime.currentDateTime().toString(
                        "yyyy-MM-dd HH:mm:ss"
                    )
                ])

                if provider.addFeature(feature):

                    loaded_count += 1

                    stored = None

                    for candidate in self.layer.getFeatures():

                        if (
                            candidate["ID"] == feature["ID"]
                            and candidate["NAME"] == feature["NAME"]
                        ):

                            stored = candidate
                            break

                    if stored is not None:
                        self.add_manager_item(stored)

            self.layer.updateExtents()
            self.layer.triggerRepaint()
            self.canvas.refresh()

            self.status.setText(
                f"Loaded {loaded_count} grid records"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Load error",
                str(error)
            )

    # ========================================================
    # CLOSE
    # ========================================================

    def closeEvent(self, event):

        # Stop map placement tool
        if self.map_tool is not None:

            self.canvas.unsetMapTool(
                self.map_tool
            )

            self.map_tool = None

        # Clear grid selection
        if self.layer is not None:
            self.layer.removeSelection()

        # Stop the exact logo instance created by this window
        if self.logo is not None:

            self.logo.stop()

            self.logo = None

        event.accept()


# ============================================================
# QGIS ENTRY POINT
# ============================================================

_fjba_basic_window = None


def main(iface):

    global _fjba_basic_window

    try:

        if (
            _fjba_basic_window is not None
            and _fjba_basic_window.isVisible()
        ):

            _fjba_basic_window.raise_()
            _fjba_basic_window.activateWindow()

            return _fjba_basic_window

        _fjba_basic_window = FjBaBasicGridGenerator(
            iface
        )

        _fjba_basic_window.show()
        _fjba_basic_window.raise_()
        _fjba_basic_window.activateWindow()

        return _fjba_basic_window

    except Exception:

        QMessageBox.critical(
            iface.mainWindow(),
            "FjBa Basic Error",
            traceback.format_exc()
        )

        return None
