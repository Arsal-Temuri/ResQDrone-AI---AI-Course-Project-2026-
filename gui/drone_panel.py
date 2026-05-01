from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QGroupBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from typing import List
from drones.drone import Drone, DroneStatus

STATUS_COLORS = {
    DroneStatus.IDLE: "#5a6a90",
    DroneStatus.SCANNING: "#4ec87e",
    DroneStatus.NAVIGATING: "#60a8e0",
    DroneStatus.RETURNING: "#c8a040",
    DroneStatus.CHARGING: "#50e0a0",
    DroneStatus.COMM_RELAY: "#a060e0",
}


class DronePanel(QWidget):

    def __init__(self, drones: List[Drone], parent=None):
        super().__init__(parent)
        self.drones = drones
        layout = QVBoxLayout(self)

        group = QGroupBox("DRONE FLEET STATUS")
        inner = QVBoxLayout(group)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "POS", "BATT%", "STATUS", "VISITED", "REWARD", "ε"]
        )
        self.table.setRowCount(len(drones))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        inner.addWidget(self.table)
        layout.addWidget(group)

    def update_drones(self, drones: List[Drone], agents: list):
        for i, drone in enumerate(drones):
            agent = agents[i] if i < len(agents) else None

            self.table.setItem(i, 0, QTableWidgetItem(str(drone.drone_id)))
            self.table.setItem(i, 1, QTableWidgetItem(f"({drone.row},{drone.col})"))

            bat_item = QTableWidgetItem(f"{drone.battery:.0f}%")
            if drone.battery < 25:
                bat_item.setForeground(QColor("#e05050"))
            elif drone.battery < 50:
                bat_item.setForeground(QColor("#c8a040"))
            else:
                bat_item.setForeground(QColor("#4ec87e"))
            self.table.setItem(i, 2, bat_item)

            status_item = QTableWidgetItem(drone.status.name)
            status_item.setForeground(
                QColor(STATUS_COLORS.get(drone.status, "#8090a8"))
            )
            self.table.setItem(i, 3, status_item)

            self.table.setItem(i, 4, QTableWidgetItem(str(drone.cells_visited)))
            self.table.setItem(i, 5, QTableWidgetItem(f"{drone.total_reward:.0f}"))

            eps_str = f"{agent.epsilon:.3f}" if agent else "—"
            self.table.setItem(i, 6, QTableWidgetItem(eps_str))
