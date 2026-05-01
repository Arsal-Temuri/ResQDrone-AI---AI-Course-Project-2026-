import random
from typing import List, Tuple
from environment.grid import DisasterGrid


class DisasterGenerator:
    """
    Generates dynamic disaster events at configurable intervals.
    Events are chosen from weighted probability pool.
    """

    EVENT_TYPES = [
        ("flood_spread", 0.35),
        ("fire_block", 0.25),
        ("comm_decay", 0.25),
        ("new_priority", 0.15),
    ]

    def __init__(self, grid: DisasterGrid):
        self.grid = grid
        self.event_history: List[dict] = []

    def _pick_event_type(self) -> str:
        roll = random.random()
        cumulative = 0.0
        for name, prob in self.EVENT_TYPES:
            cumulative += prob
            if roll <= cumulative:
                return name
        return "flood_spread"

    def _pick_target_cell(self, event_type: str) -> Tuple[int, int]:
        """Pick a cell appropriate for the event type."""
        from environment.cell import CellState

        candidates = []
        if event_type == "flood_spread":
            candidates = [
                (c.row, c.col)
                for c in self.grid.all_cells()
                if c.state in (CellState.NORMAL, CellState.AFFECTED)
            ]
        elif event_type == "fire_block":
            candidates = [
                (c.row, c.col)
                for c in self.grid.all_cells()
                if c.state in (CellState.AFFECTED, CellState.NORMAL)
            ]
        elif event_type == "comm_decay":
            candidates = [
                (c.row, c.col)
                for c in self.grid.all_cells()
                if c.state != CellState.BASE
            ]
        elif event_type == "new_priority":
            candidates = [
                (c.row, c.col)
                for c in self.grid.all_cells()
                if c.state == CellState.AFFECTED
            ]
        if not candidates:
            return (
                random.randint(1, self.grid.rows - 2),
                random.randint(1, self.grid.cols - 2),
            )
        return random.choice(candidates)

    def generate_event(self, tick: int) -> dict:
        """Generate and apply one random disaster event. Returns event record."""
        event_type = self._pick_event_type()
        r, c = self._pick_target_cell(event_type)
        self.grid.apply_event(event_type, r, c)
        record = {"tick": tick, "type": event_type, "row": r, "col": c}
        self.event_history.append(record)
        return record
