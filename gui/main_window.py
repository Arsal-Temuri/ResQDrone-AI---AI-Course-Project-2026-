from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QSplitter,
)
from PyQt6.QtCore import QTimer, Qt
from simulation.engine import SimulationEngine
from gui.grid_canvas import GridCanvas
from gui.control_panel import ControlPanel
from gui.drone_panel import DronePanel
from gui.metrics_panel import MetricsPanel
from gui.event_log import EventLog
from gui.legend import LegendWidget
from gui.styles import MAIN_STYLE
from config.settings import TICK_INTERVAL_MS
from typing import Optional


class MainWindow(QMainWindow):

    def __init__(self, engine: Optional[SimulationEngine] = None):
        super().__init__()
        self.setWindowTitle("Multi-Drone Disaster Response System")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(MAIN_STYLE)

        # Simulation engine (use provided or create new)
        self.engine = engine if engine is not None else SimulationEngine()

        # Timer for simulation ticks
        self.timer = QTimer(self)
        self.timer.setInterval(TICK_INTERVAL_MS)
        self.timer.timeout.connect(self._tick)

        # Build UI
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setSpacing(8)
        root_layout.setContentsMargins(8, 8, 8, 8)

        # LEFT PANEL: controls + drone table + event log
        left_widget = QWidget()
        left_widget.setFixedWidth(340)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(6)

        self.control_panel = ControlPanel()
        self.control_panel.sig_start.connect(self._start)
        self.control_panel.sig_pause.connect(self._pause)
        self.control_panel.sig_reset.connect(self._reset)
        self.control_panel.sig_speed_changed.connect(self._set_speed)
        self.control_panel.sig_toggle_comm.connect(self._toggle_comm)
        self.control_panel.sig_toggle_paths.connect(self._toggle_paths)
        self.control_panel.sig_randomize_grid.connect(self._randomize_grid)
        self.control_panel.sig_zoom_in.connect(self._zoom_in)
        self.control_panel.sig_zoom_out.connect(self._zoom_out)
        self.control_panel.sig_fit_window.connect(self._fit_window)
        left_layout.addWidget(self.control_panel)

        self.drone_panel = DronePanel(self.engine.swarm.drones)
        left_layout.addWidget(self.drone_panel)

        self.event_log = EventLog()
        left_layout.addWidget(self.event_log)

        root_layout.addWidget(left_widget)

        # CENTER: grid canvas (no scrolling, expands to fit)
        self.grid_canvas = GridCanvas(self.engine.grid, self.engine.swarm.drones)
        root_layout.addWidget(self.grid_canvas, 1)

        # CENTER-RIGHT: Legend panel (fixed width)
        self.legend = LegendWidget()
        root_layout.addWidget(self.legend)

        # RIGHT PANEL: metrics charts (fixed width)
        self.metrics_panel = MetricsPanel(self.engine.metrics)
        self.metrics_panel.setFixedWidth(340)
        root_layout.addWidget(self.metrics_panel)

    def _tick(self):
        snapshot = self.engine.tick()
        self.grid_canvas.refresh()
        self.drone_panel.update_drones(
            self.engine.swarm.drones, self.engine.swarm.agents
        )
        self.metrics_panel.refresh()
        events = snapshot.get("recent_events", [])
        self.event_log.append_events(events[:3])

    def _start(self):
        self.engine.start()
        self.timer.start()

    def _pause(self):
        self.engine.pause()
        if self.engine.paused:
            self.timer.stop()
        else:
            self.timer.start()

    def _reset(self):
        self.timer.stop()
        self.engine.reset()
        # After reset, grid stays the same but drones/metrics are rebuilt
        self.grid_canvas.grid = self.engine.grid
        self.grid_canvas.drones = self.engine.swarm.drones
        self.grid_canvas.hovered_cell = None
        self.grid_canvas.selected_cell = None
        self.drone_panel.drones = self.engine.swarm.drones
        self.metrics_panel.metrics = self.engine.metrics
        self.event_log.clear()
        self.grid_canvas.refresh()
        self.drone_panel.update_drones(
            self.engine.swarm.drones, self.engine.swarm.agents
        )

    def _randomize_grid(self):
        was_running = self.timer.isActive()
        self.timer.stop()
        self.engine.randomize_grid()
        self.grid_canvas.grid = self.engine.grid
        self.grid_canvas.drones = self.engine.swarm.drones
        self.grid_canvas.hovered_cell = None
        self.grid_canvas.selected_cell = None
        self.drone_panel.drones = self.engine.swarm.drones
        self.metrics_panel.metrics = self.engine.metrics
        self.event_log.clear()
        self.grid_canvas.refresh()
        self.drone_panel.update_drones(
            self.engine.swarm.drones, self.engine.swarm.agents
        )
        self.metrics_panel.refresh()
        if was_running:
            self.engine.start()
            self.timer.start()

    def _set_speed(self, ms: int):
        self.timer.setInterval(ms)

    def _toggle_comm(self, show: bool):
        self.grid_canvas.toggle_comm_overlay(show)

    def _toggle_paths(self, show: bool):
        self.grid_canvas.toggle_paths(show)

    def _zoom_in(self):
        self.grid_canvas.zoom_in()

    def _zoom_out(self):
        self.grid_canvas.zoom_out()

    def _fit_window(self):
        self.grid_canvas.fit_to_window()
