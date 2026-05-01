from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSlider,
    QComboBox,
    QCheckBox,
    QGroupBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from config.settings import TICK_INTERVAL_MS


class ControlPanel(QWidget):
    sig_start = pyqtSignal()
    sig_pause = pyqtSignal()
    sig_reset = pyqtSignal()
    sig_speed_changed = pyqtSignal(int)
    sig_toggle_comm = pyqtSignal(bool)
    sig_toggle_paths = pyqtSignal(bool)
    sig_zoom_in = pyqtSignal()
    sig_zoom_out = pyqtSignal()
    sig_fit_window = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Title
        title = QLabel("DRONE SWARM CONTROL")
        title.setObjectName("label_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Control buttons
        btn_group = QGroupBox("SIMULATION")
        btn_layout = QHBoxLayout(btn_group)

        self.btn_start = QPushButton("▶ START")
        self.btn_start.setObjectName("btn_start")
        self.btn_pause = QPushButton("⏸ PAUSE")
        self.btn_pause.setObjectName("btn_pause")
        self.btn_reset = QPushButton("⟳ RESET")
        self.btn_reset.setObjectName("btn_reset")

        self.btn_start.clicked.connect(self.sig_start.emit)
        self.btn_pause.clicked.connect(self.sig_pause.emit)
        self.btn_reset.clicked.connect(self.sig_reset.emit)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_reset)
        layout.addWidget(btn_group)

        # Speed control
        speed_group = QGroupBox("SPEED")
        speed_layout = QVBoxLayout(speed_group)
        self.speed_label = QLabel(f"Tick: {TICK_INTERVAL_MS}ms")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(2000)
        self.speed_slider.setValue(TICK_INTERVAL_MS)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_slider)
        layout.addWidget(speed_group)

        # Overlay options
        overlay_group = QGroupBox("OVERLAYS")
        overlay_layout = QVBoxLayout(overlay_group)

        self.chk_comm = QCheckBox("Signal strength overlay")
        self.chk_comm.toggled.connect(self.sig_toggle_comm.emit)
        self.chk_paths = QCheckBox("Show planned paths")
        self.chk_paths.setChecked(True)
        self.chk_paths.toggled.connect(self.sig_toggle_paths.emit)

        overlay_layout.addWidget(self.chk_comm)
        overlay_layout.addWidget(self.chk_paths)
        layout.addWidget(overlay_group)

        # Zoom controls
        zoom_group = QGroupBox("GRID VIEW")
        zoom_layout = QHBoxLayout(zoom_group)

        self.btn_zoom_in = QPushButton("🔍+")
        self.btn_zoom_in.setMaximumWidth(70)
        self.btn_zoom_in.clicked.connect(self.sig_zoom_in.emit)

        self.btn_zoom_out = QPushButton("🔍−")
        self.btn_zoom_out.setMaximumWidth(70)
        self.btn_zoom_out.clicked.connect(self.sig_zoom_out.emit)

        self.btn_fit = QPushButton("Fit Window")
        self.btn_fit.clicked.connect(self.sig_fit_window.emit)

        zoom_layout.addWidget(self.btn_zoom_in)
        zoom_layout.addWidget(self.btn_zoom_out)
        zoom_layout.addWidget(self.btn_fit)
        layout.addWidget(zoom_group)

        layout.addStretch()

    def _on_speed_changed(self, val: int):
        self.speed_label.setText(f"Tick: {val}ms")
        self.sig_speed_changed.emit(val)
