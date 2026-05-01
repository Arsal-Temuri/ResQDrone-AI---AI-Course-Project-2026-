# Dark-themed QSS stylesheet — industrial/utilitarian disaster-ops aesthetic

MAIN_STYLE = """
QMainWindow, QWidget {
    background-color: #12141a;
    color: #c8ccd6;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}

QGroupBox {
    border: 1px solid #2a2d38;
    border-radius: 6px;
    margin-top: 8px;
    padding: 6px;
    color: #6e7a94;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}

QPushButton {
    background-color: #1e2130;
    border: 1px solid #2e3248;
    border-radius: 4px;
    padding: 6px 16px;
    color: #8fa3c8;
    font-size: 11px;
}

QPushButton:hover {
    background-color: #252840;
    border-color: #4a5580;
    color: #c0d0f0;
}

QPushButton:pressed {
    background-color: #1a1d2c;
}

QPushButton#btn_start {
    background-color: #1a3020;
    border-color: #2a5535;
    color: #4ec87e;
}

QPushButton#btn_start:hover {
    background-color: #1f3a26;
    border-color: #3a7048;
}

QPushButton#btn_pause {
    background-color: #302814;
    border-color: #554525;
    color: #c8a040;
}

QPushButton#btn_reset {
    background-color: #301818;
    border-color: #552525;
    color: #c84040;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #2a2d38;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #5a6a90;
    width: 12px;
    height: 12px;
    border-radius: 6px;
    margin: -4px 0;
}

QTableWidget {
    background-color: #0e1016;
    border: 1px solid #1e2130;
    gridline-color: #1a1d28;
    selection-background-color: #1e2a40;
}

QTableWidget::item {
    padding: 4px;
}

QHeaderView::section {
    background-color: #1a1d28;
    border: none;
    border-right: 1px solid #2a2d38;
    padding: 4px 8px;
    color: #5a6a80;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QScrollBar:vertical {
    background: #12141a;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #2a2d38;
    border-radius: 4px;
}

QLabel#label_title {
    font-size: 16px;
    font-weight: bold;
    color: #7090d0;
    letter-spacing: 2px;
}

QLabel#label_stats {
    color: #4ec87e;
    font-size: 13px;
    font-weight: bold;
}

QTextEdit {
    background-color: #0a0c10;
    border: 1px solid #1e2130;
    color: #8090a8;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}

QComboBox {
    background-color: #1e2130;
    border: 1px solid #2e3248;
    border-radius: 4px;
    padding: 4px 8px;
    color: #8fa3c8;
}
"""
