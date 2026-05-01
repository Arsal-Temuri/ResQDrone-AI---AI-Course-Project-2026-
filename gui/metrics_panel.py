from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from simulation.metrics_tracker import MetricsTracker

pg.setConfigOption("background", "#0a0c10")
pg.setConfigOption("foreground", "#5a6a80")


class MetricsPanel(QWidget):

    def __init__(self, metrics: MetricsTracker, parent=None):
        super().__init__(parent)
        self.metrics = metrics
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Summary stats labels
        stats_group = QGroupBox("LIVE METRICS")
        stats_layout = QHBoxLayout(stats_group)
        self.lbl_coverage = QLabel("Coverage: 0%")
        self.lbl_coverage.setObjectName("label_stats")
        self.lbl_priority = QLabel("Priority: 0%")
        self.lbl_priority.setObjectName("label_stats")
        self.lbl_battery = QLabel("Avg Batt: 100%")
        self.lbl_battery.setObjectName("label_stats")
        stats_layout.addWidget(self.lbl_coverage)
        stats_layout.addWidget(self.lbl_priority)
        stats_layout.addWidget(self.lbl_battery)
        layout.addWidget(stats_group)

        # Coverage chart
        cov_group = QGroupBox("COVERAGE OVER TIME")
        cov_layout = QVBoxLayout(cov_group)
        self.coverage_plot = pg.PlotWidget()
        self.coverage_plot.setMaximumHeight(120)
        self.coverage_plot.showGrid(x=False, y=True, alpha=0.2)
        self.coverage_curve = self.coverage_plot.plot(pen=pg.mkPen("#4ec87e", width=2))
        self.priority_curve = self.coverage_plot.plot(
            pen=pg.mkPen("#e05050", width=1, style=Qt.PenStyle.DashLine)
        )
        cov_layout.addWidget(self.coverage_plot)
        layout.addWidget(cov_group)

        # Reward chart
        rew_group = QGroupBox("AVG Q-LEARNING REWARD")
        rew_layout = QVBoxLayout(rew_group)
        self.reward_plot = pg.PlotWidget()
        self.reward_plot.setMaximumHeight(100)
        self.reward_plot.showGrid(x=False, y=True, alpha=0.2)
        self.reward_curve = self.reward_plot.plot(pen=pg.mkPen("#7090d0", width=2))
        rew_layout.addWidget(self.reward_plot)
        layout.addWidget(rew_group)

        # Battery chart
        bat_group = QGroupBox("FLEET AVERAGE BATTERY")
        bat_layout = QVBoxLayout(bat_group)
        self.battery_plot = pg.PlotWidget()
        self.battery_plot.setMaximumHeight(100)
        self.battery_plot.showGrid(x=False, y=True, alpha=0.2)
        self.battery_curve = self.battery_plot.plot(pen=pg.mkPen("#c8a040", width=2))
        bat_layout.addWidget(self.battery_plot)
        layout.addWidget(bat_group)

    def refresh(self):
        latest = self.metrics.latest()
        if not latest:
            return

        cov = latest.get("coverage", 0)
        pri = latest.get("priority_coverage", 0)
        bat = latest.get("avg_battery", 0)

        self.lbl_coverage.setText(f"Coverage: {cov * 100:.1f}%")
        self.lbl_priority.setText(f"Priority: {pri * 100:.1f}%")
        self.lbl_battery.setText(f"Avg Batt: {bat:.0f}%")

        cov_series = self.metrics.get_series("coverage")
        pri_series = self.metrics.get_series("priority_coverage")
        rew_series = self.metrics.get_series("avg_reward")
        bat_series = self.metrics.get_series("avg_battery")

        xs = list(range(len(cov_series)))
        if xs:
            self.coverage_curve.setData(xs, cov_series)
            self.priority_curve.setData(xs, pri_series)
        if rew_series:
            self.reward_curve.setData(list(range(len(rew_series))), rew_series)
        if bat_series:
            self.battery_curve.setData(list(range(len(bat_series))), bat_series)
