import random
import numpy as np
from typing import List, Tuple, Optional
from environment.cell import Cell, CellState


class DisasterGrid:
    """
    2D grid representing the disaster environment.
    Supports dynamic state transitions and cell queries.
    """

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.tick = 0
        self.cells: List[List[Cell]] = [
            [Cell(r, c) for c in range(cols)] for r in range(rows)
        ]
        self._base_positions: List[Tuple[int, int]] = []
        self._initialize_default_layout()

    def _initialize_default_layout(self):
        """Place base stations in corners and scatter initial disaster zones."""
        corners = [
            (0, 0),
            (0, self.cols - 1),
            (self.rows - 1, 0),
            (self.rows - 1, self.cols - 1),
        ]
        for r, c in corners:
            self.cells[r][c].state = CellState.BASE
            self._base_positions.append((r, c))

        # Scatter affected zones (15% of cells)
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c].state == CellState.BASE:
                    continue
                roll = random.random()
                if roll < 0.08:
                    self.cells[r][c].state = CellState.HIGH_PRIORITY
                    self.cells[r][c].severity = random.uniform(0.6, 1.0)
                elif roll < 0.18:
                    self.cells[r][c].state = CellState.AFFECTED
                elif roll < 0.24:
                    self.cells[r][c].state = CellState.BLOCKED
                elif roll < 0.30:
                    self.cells[r][c].state = CellState.COMM_RISK
                    self.cells[r][c].comm_strength = random.uniform(0.1, 0.5)

    def get_cell(self, r: int, c: int) -> Optional[Cell]:
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.cells[r][c]
        return None

    def neighbors(self, r: int, c: int) -> List[Cell]:
        """Return traversable 4-directional neighbors."""
        candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [
            self.cells[nr][nc]
            for nr, nc in candidates
            if 0 <= nr < self.rows
            and 0 <= nc < self.cols
            and self.cells[nr][nc].state != CellState.BLOCKED
        ]

    def all_cells(self) -> List[Cell]:
        return [self.cells[r][c] for r in range(self.rows) for c in range(self.cols)]

    def get_base_positions(self) -> List[Tuple[int, int]]:
        return self._base_positions

    def nearest_base(self, r: int, c: int) -> Tuple[int, int]:
        return min(self._base_positions, key=lambda b: abs(b[0] - r) + abs(b[1] - c))

    def coverage_rate(self) -> float:
        """Fraction of non-blocked, non-base cells that have been visited."""
        targets = [
            cell
            for cell in self.all_cells()
            if cell.state not in (CellState.BLOCKED, CellState.BASE)
        ]
        if not targets:
            return 1.0
        visited = sum(1 for cell in targets if cell.visited)
        return visited / len(targets)

    def priority_coverage_rate(self) -> float:
        """Fraction of HIGH_PRIORITY cells visited."""
        hp = [c for c in self.all_cells() if c.state == CellState.HIGH_PRIORITY]
        if not hp:
            return 1.0
        return sum(1 for c in hp if c.visited) / len(hp)

    def mark_visited(self, r: int, c: int, tick: int):
        cell = self.cells[r][c]
        cell.visited = True
        cell.visit_count += 1
        cell.last_visited_tick = tick

    def apply_event(self, event_type: str, r: int, c: int):
        """Apply a dynamic disaster event to a cell."""
        cell = self.get_cell(r, c)
        if not cell or cell.state == CellState.BASE:
            return
        if event_type == "flood_spread":
            if cell.state == CellState.NORMAL:
                cell.state = CellState.AFFECTED
        elif event_type == "fire_block":
            if cell.state in (CellState.AFFECTED, CellState.NORMAL):
                cell.state = CellState.BLOCKED
        elif event_type == "comm_decay":
            cell.comm_strength = max(0.0, cell.comm_strength - random.uniform(0.1, 0.3))
            if cell.comm_strength < 0.5 and cell.state == CellState.NORMAL:
                cell.state = CellState.COMM_RISK
        elif event_type == "new_priority":
            if cell.state == CellState.AFFECTED:
                cell.state = CellState.HIGH_PRIORITY
                cell.severity = random.uniform(0.7, 1.0)

    def to_state_matrix(self) -> np.ndarray:
        """Return integer state matrix for Q-Learning state encoding."""
        return np.array([[cell.state.value for cell in row] for row in self.cells])
