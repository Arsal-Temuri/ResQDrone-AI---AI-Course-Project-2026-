from PyQt6.QtWidgets import QWidget, QToolTip, QSizePolicy
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from environment.grid import DisasterGrid
from environment.cell import CellState, CELL_COLORS, CELL_LABELS
from drones.drone import Drone, DroneStatus
from typing import List, Optional, Tuple
from config.settings import CELL_SIZE_PX
import math

# Drone color palette (one per drone)
DRONE_COLORS = [
    (80, 180, 240),  # cyan-blue
    (240, 160, 40),  # amber
    (160, 240, 100),  # green
    (240, 80, 140),  # pink
    (160, 120, 240),  # purple
    (240, 200, 60),  # yellow
    (60, 200, 180),  # teal
    (240, 100, 60),  # orange
]


class GridCanvas(QWidget):
    """
    Main animated grid widget. Renders:
    - Cell states with colors
    - Drone positions with colored circles and IDs
    - Planned paths as dotted lines
    - Battery level mini-bar per drone
    - Visited cell tick marks
    - Communication strength overlay (optional)
    """

    def __init__(self, grid: DisasterGrid, drones: List[Drone], parent=None):
        super().__init__(parent)
        self.grid = grid
        self.drones = drones
        self.show_comm_overlay = False
        self.show_paths = True
        self.show_visited = True
        self.hovered_cell: Optional[Tuple[int, int]] = None
        self.selected_cell: Optional[Tuple[int, int]] = None

        # Zoom and scaling
        self.zoom_level = 1.0  # Multiplier for cell size
        self.min_zoom = 0.3
        self.max_zoom = 3.0
        self.auto_fit = True

        self.setMouseTracking(True)  # Enable mouse tracking
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def get_cell_size(self):
        """Calculate cell size based on zoom level and available space."""
        if self.auto_fit:
            # Calculate cell size to fit available space
            available_width = max(100, self.width() - 20)
            available_height = max(100, self.height() - 20)

            cols_fit = available_width / self.grid.cols
            rows_fit = available_height / self.grid.rows

            return int(min(cols_fit, rows_fit))
        else:
            # Use zoom level to scale from base cell size
            return max(5, int(CELL_SIZE_PX * self.zoom_level))

    def zoom_in(self):
        """Increase zoom level."""
        self.auto_fit = False
        self.zoom_level = min(self.max_zoom, self.zoom_level * 1.2)
        self.update()

    def zoom_out(self):
        """Decrease zoom level."""
        self.auto_fit = False
        self.zoom_level = max(self.min_zoom, self.zoom_level / 1.2)
        self.update()

    def fit_to_window(self):
        """Enable auto-fit mode."""
        self.auto_fit = True
        self.update()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cs = self.get_cell_size()

        # Draw cells
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                cell = self.grid.cells[r][c]
                base_rgb = CELL_COLORS[cell.state]
                color = QColor(*base_rgb)

                # Lighten visited cells slightly
                if cell.visited and cell.state not in (
                    CellState.BASE,
                    CellState.BLOCKED,
                ):
                    color = color.lighter(120)

                # Communication overlay
                if self.show_comm_overlay and cell.comm_strength < 0.5:
                    alpha = int((1.0 - cell.comm_strength) * 80)
                    color = QColor(100, 60, 160, 200)

                rect = QRect(c * cs, r * cs, cs - 1, cs - 1)
                painter.fillRect(rect, QBrush(color))

                # Highlight hovered cell (bright border)
                if self.hovered_cell == (r, c):
                    painter.setPen(QPen(QColor(200, 200, 100), 2))
                    painter.drawRect(rect)

                # Highlight selected cell (thick colored border)
                if self.selected_cell == (r, c):
                    painter.setPen(QPen(QColor(100, 200, 255), 3))
                    painter.drawRect(rect)

                # Cell label (small, center) - scale font size
                painter.setPen(QPen(QColor(120, 130, 150)))
                font_size = (
                    max(5, int(7 * self.zoom_level))
                    if not self.auto_fit
                    else max(5, int(7 * cs / CELL_SIZE_PX))
                )
                painter.setFont(QFont("Consolas", font_size))
                painter.drawText(
                    rect, Qt.AlignmentFlag.AlignCenter, CELL_LABELS[cell.state]
                )

                # Visited checkmark
                if self.show_visited and cell.visited:
                    painter.setPen(QPen(QColor(80, 200, 120, 120)))
                    painter.setFont(
                        QFont("Consolas", max(5, int(8 * cs / CELL_SIZE_PX)))
                    )
                    painter.drawText(
                        rect.adjusted(2, 2, 0, 0),
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                        "✓",
                    )

        # Draw drone paths (dotted lines)
        if self.show_paths:
            for i, drone in enumerate(self.drones):
                if drone.current_path:
                    dc = DRONE_COLORS[i % len(DRONE_COLORS)]
                    pen = QPen(QColor(*dc, 100))
                    pen.setStyle(Qt.PenStyle.DotLine)
                    pen.setWidth(1)
                    painter.setPen(pen)
                    prev = (drone.col * cs + cs // 2, drone.row * cs + cs // 2)
                    for pr, pc in drone.current_path:
                        curr = (pc * cs + cs // 2, pr * cs + cs // 2)
                        painter.drawLine(prev[0], prev[1], curr[0], curr[1])
                        prev = curr

        # Draw drones
        for i, drone in enumerate(self.drones):
            dc = DRONE_COLORS[i % len(DRONE_COLORS)]
            cx = drone.col * cs + cs // 2
            cy = drone.row * cs + cs // 2
            radius = max(2, cs // 3)

            # Outer glow ring for status
            if drone.status == DroneStatus.CHARGING:
                glow = QColor(80, 200, 80, 60)
                painter.setBrush(QBrush(glow))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPoint(cx, cy), radius + 4, radius + 4)
            elif drone.is_low_battery():
                glow = QColor(220, 60, 60, 80)
                painter.setBrush(QBrush(glow))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPoint(cx, cy), radius + 4, radius + 4)

            # Drone body
            painter.setBrush(QBrush(QColor(*dc)))
            painter.setPen(QPen(QColor(200, 210, 230), 1))
            painter.drawEllipse(QPoint(cx, cy), radius, radius)

            # Drone ID
            painter.setPen(QPen(QColor(10, 12, 18)))
            font_size = max(5, int(8 * cs / CELL_SIZE_PX))
            painter.setFont(QFont("Consolas", font_size, QFont.Weight.Bold))
            painter.drawText(
                QRect(cx - radius, cy - radius, radius * 2, radius * 2),
                Qt.AlignmentFlag.AlignCenter,
                str(i),
            )

            # Battery bar (below drone)
            bar_w = cs - 6
            bar_h = max(2, cs // 8)
            bar_x = drone.col * cs + 3
            bar_y = drone.row * cs + cs - 5
            # Background
            painter.fillRect(QRect(bar_x, bar_y, bar_w, bar_h), QColor(30, 32, 40))
            # Fill
            fill_w = int(bar_w * drone.battery / 100.0)
            bat_color = (
                QColor(80, 200, 80)
                if drone.battery > 50
                else QColor(220, 180, 40) if drone.battery > 25 else QColor(220, 60, 60)
            )
            painter.fillRect(QRect(bar_x, bar_y, fill_w, bar_h), bat_color)

    def toggle_comm_overlay(self, show: bool):
        self.show_comm_overlay = show
        self.update()

    def toggle_paths(self, show: bool):
        self.show_paths = show
        self.update()

    def refresh(self):
        self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse hover - show tooltip with cell info."""
        cs = self.get_cell_size()
        pos = event.pos()
        col = pos.x() // cs
        row = pos.y() // cs

        # Check bounds
        if 0 <= row < self.grid.rows and 0 <= col < self.grid.cols:
            self.hovered_cell = (row, col)
            cell = self.grid.cells[row][col]

            # Show tooltip with coordinates and cell type
            state_name = cell.state.name
            comm_str = f"Comm: {cell.comm_strength:.1%}"
            tooltip = f"Cell ({row}, {col})\n{state_name}\n{comm_str}"

            QToolTip.showText(event.globalPosition().toPoint(), tooltip, self)
            self.update()
        else:
            self.hovered_cell = None
            QToolTip.hideText()
            self.update()

    def mousePressEvent(self, event):
        """Handle click - select cell."""
        cs = self.get_cell_size()
        pos = event.pos()
        col = pos.x() // cs
        row = pos.y() // cs

        # Check bounds
        if 0 <= row < self.grid.rows and 0 <= col < self.grid.cols:
            if self.selected_cell == (row, col):
                # Deselect if clicking same cell
                self.selected_cell = None
            else:
                # Select new cell
                self.selected_cell = (row, col)
                cell = self.grid.cells[row][col]
                state_name = cell.state.name
                tooltip = f"Selected: ({row}, {col}) - {state_name}"
                QToolTip.showText(
                    event.globalPosition().toPoint(), tooltip, self, self.rect()
                )
            self.update()
