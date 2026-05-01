import pytest
from environment.grid import DisasterGrid
from environment.cell import CellState
from algorithms.genetic.ga_optimizer import GAOptimizer


def test_ga_returns_valid_assignment():
    grid = DisasterGrid(10, 10)
    ga = GAOptimizer(grid, num_drones=4, num_zones=4)
    assignment = ga.run()
    assert len(assignment) == 4
    assert all(0 <= z < 4 for z in assignment)


def test_ga_zones_cover_grid():
    grid = DisasterGrid(10, 10)
    ga = GAOptimizer(grid, num_drones=3, num_zones=3)
    all_zone_cells = set()
    for zone in ga.zones:
        for cell in zone:
            all_zone_cells.add(cell)
    # All non-base cells should be in some zone
    non_base = [
        (r, c)
        for r in range(10)
        for c in range(10)
        if grid.cells[r][c].state != CellState.BASE
    ]
    for pos in non_base:
        assert pos in all_zone_cells
