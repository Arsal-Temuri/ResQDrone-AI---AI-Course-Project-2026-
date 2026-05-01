from enum import Enum, auto
from dataclasses import dataclass, field


class CellState(Enum):
    NORMAL = auto()
    AFFECTED = auto()
    HIGH_PRIORITY = auto()
    BLOCKED = auto()
    COMM_RISK = auto()
    BASE = auto()


# Color mapping for GUI rendering (RGB tuples)
CELL_COLORS = {
    CellState.NORMAL: (45, 50, 60),
    CellState.AFFECTED: (180, 100, 30),
    CellState.HIGH_PRIORITY: (200, 40, 40),
    CellState.BLOCKED: (20, 20, 25),
    CellState.COMM_RISK: (80, 60, 120),
    CellState.BASE: (30, 120, 80),
}

CELL_LABELS = {
    CellState.NORMAL: "N",
    CellState.AFFECTED: "A",
    CellState.HIGH_PRIORITY: "H",
    CellState.BLOCKED: "X",
    CellState.COMM_RISK: "C",
    CellState.BASE: "B",
}


@dataclass
class Cell:
    row: int
    col: int
    state: CellState = CellState.NORMAL
    visited: bool = False
    visit_count: int = 0
    comm_strength: float = 1.0  # 0.0 = dead zone, 1.0 = full signal
    severity: float = 0.0  # 0.0–1.0, used for HIGH_PRIORITY cells
    last_visited_tick: int = -1

    def is_traversable(self) -> bool:
        return self.state != CellState.BLOCKED

    def risk_cost(self) -> float:
        """Returns extra A* cost for entering this cell."""
        from config.settings import (
            COST_RISK_AFFECTED,
            COST_COMM_PENALTY,
            COST_RISK_HIGH_PRIORITY,
        )

        cost = 0.0
        if self.state == CellState.AFFECTED:
            cost += COST_RISK_AFFECTED
        elif self.state == CellState.HIGH_PRIORITY:
            cost += COST_RISK_HIGH_PRIORITY
        if self.comm_strength < 0.5:
            cost += COST_COMM_PENALTY * (1.0 - self.comm_strength)
        return cost
