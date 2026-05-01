import math
import numpy as np
from environment.grid import DisasterGrid


class CommunicationMap:
    """
    Models signal strength across the grid.
    Signal degrades with distance from communication towers.
    Also affected by BLOCKED cells (line of sight obstruction).
    """

    def __init__(self, grid: DisasterGrid, tower_positions=None):
        self.grid = grid
        # Default towers at grid center and near bases
        if tower_positions is None:
            cr, cc = grid.rows // 2, grid.cols // 2
            self.towers = [
                (cr, cc),
                (0, cc),
                (cr, 0),
                (grid.rows - 1, cc),
                (cr, grid.cols - 1),
            ]
        else:
            self.towers = tower_positions
        self.signal_map = np.ones((grid.rows, grid.cols), dtype=float)
        self.recompute()

    def recompute(self):
        """Recompute signal strength for every cell based on tower proximity."""
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                cell = self.grid.cells[r][c]
                best_signal = 0.0
                for tr, tc in self.towers:
                    dist = math.sqrt((r - tr) ** 2 + (c - tc) ** 2)
                    signal = max(
                        0.0, 1.0 - dist / (max(self.grid.rows, self.grid.cols) * 0.6)
                    )
                    best_signal = max(best_signal, signal)
                # Apply existing cell comm_strength modifier
                self.signal_map[r][c] = best_signal * cell.comm_strength
                cell.comm_strength = self.signal_map[r][c]

    def get_signal(self, r: int, c: int) -> float:
        return float(self.signal_map[r][c])
