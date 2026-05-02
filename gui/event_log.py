from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QGroupBox
from PyQt6.QtGui import QTextCursor, QColor
from typing import List

EVENT_COLORS = {
    "flood_spread": "#4080c0",
    "fire_block": "#e05050",
    "comm_decay": "#9060c0",
    "new_priority": "#e08030",
    "charging": "#40c080",
    "replan": "#c0a040",
}


class EventLog(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        group = QGroupBox("EVENT LOG")
        inner = QVBoxLayout(group)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(180)
        inner.addWidget(self.log)
        layout.addWidget(group)

    def append_events(self, events: List[dict]):
        for ev in reversed(events):
            ev_type = ev.get("type", "unknown")
            tick = ev.get("tick", "?")
            color = EVENT_COLORS.get(ev_type, "#8090a8")

            if ev_type in ("flood_spread", "fire_block", "comm_decay", "new_priority"):
                r, c = ev.get("row", "?"), ev.get("col", "?")
                msg = f'<span style="color:{color}">[T{tick}] {ev_type.upper()} @ ({r},{c})</span>'
            elif ev_type == "charging":
                did = ev.get("drone_id", "?")
                msg = (
                    f'<span style="color:{color}">[T{tick}] DRONE {did} CHARGING</span>'
                )
            elif ev_type == "replan":
                did = ev.get("drone_id", "?")
                msg = f'<span style="color:{color}">[T{tick}] DRONE {did} REPLANNING</span>'
            else:
                msg = f'<span style="color:#6070a0">[T{tick}] {ev}</span>'

            self.log.insertHtml(msg + "<br>")

        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.log.setTextCursor(cursor)

    def clear(self):
        self.log.clear()
