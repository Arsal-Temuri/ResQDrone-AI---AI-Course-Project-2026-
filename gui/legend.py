from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QColor, QPixmap, QPainter, QFont
from PyQt6.QtCore import Qt
from environment.cell import CELL_COLORS, CELL_LABELS, CellState
from config.settings import CELL_SIZE_PX


class LegendWidget(QWidget):
    """
    Legend panel showing cell type meanings with colors and labels.
    Displays all 6 cell state types with their visual representations.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(200)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Title
        title = QLabel("Cell Legend")
        title.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #8fa3c8;")
        layout.addWidget(title)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #4a5a7a;")
        layout.addWidget(sep)

        # Legend items for each cell type
        cell_types = [
            (CellState.NORMAL, "Normal Zone", "Safe area"),
            (CellState.HIGH_PRIORITY, "High Priority", "Requires help"),
            (CellState.AFFECTED, "Affected Zone", "Disaster area"),
            (CellState.COMM_RISK, "Comm Risk", "Signal weak"),
            (CellState.BLOCKED, "Blocked", "Not traversable"),
            (CellState.BASE, "Base Station", "Charging point"),
        ]

        for cell_state, name, description in cell_types:
            item_layout = QVBoxLayout()
            item_layout.setSpacing(3)

            # Color box + label
            header_layout = self._create_legend_item(cell_state, name)
            item_layout.addLayout(header_layout)

            # Description
            desc = QLabel(description)
            desc.setFont(QFont("Consolas", 8))
            desc.setStyleSheet("color: #a0a8b8; margin-left: 28px;")
            desc.setWordWrap(True)
            item_layout.addWidget(desc)

            # Add to main layout
            layout.addLayout(item_layout)

        layout.addStretch()

        # Info section
        info_sep = QFrame()
        info_sep.setFrameShape(QFrame.Shape.HLine)
        info_sep.setStyleSheet("color: #4a5a7a;")
        layout.addWidget(info_sep)

        info_label = QLabel("Interactions")
        info_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        info_label.setStyleSheet("color: #8fa3c8; margin-top: 8px;")
        layout.addWidget(info_label)

        hover_info = QLabel("🖱️ Hover: See cell info\n\n👆 Click: Select cell")
        hover_info.setFont(QFont("Consolas", 8))
        hover_info.setStyleSheet("color: #a0a8b8; line-height: 1.5;")
        hover_info.setWordWrap(True)
        layout.addWidget(hover_info)

    def _create_legend_item(self, cell_state: CellState, label: str):
        """Create a legend item with color box and label."""
        layout = QVBoxLayout()
        layout.setSpacing(0)

        # Create color box pixmap
        pixmap = QPixmap(20, 20)
        rgb = CELL_COLORS[cell_state]
        painter = QPainter(pixmap)
        painter.fillRect(pixmap.rect(), QColor(*rgb))
        painter.drawRect(0, 0, 19, 19)
        painter.end()

        # Header with color and label
        header = QVBoxLayout()
        header.setSpacing(0)
        header.setContentsMargins(0, 0, 0, 0)

        # Color box + name
        color_name_layout = QVBoxLayout()
        color_name_layout.setSpacing(5)
        color_name_layout.setContentsMargins(0, 0, 0, 0)

        # Show color box
        color_box = QLabel()
        color_box.setPixmap(pixmap)

        name_label = QLabel(label)
        name_label.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #c8d8e8;")

        # Combine in horizontal layout
        h_layout = QVBoxLayout()
        h_layout.setSpacing(5)
        h_layout.addWidget(name_label)

        return h_layout
