import pytest
from environment.grid import DisasterGrid
from environment.cell import CellState
from algorithms.astar.astar import astar, heuristic


def make_clean_grid():
    g = DisasterGrid(10, 10)
    for r in range(g.rows):
        for c in range(g.cols):
            g.cells[r][c].state = CellState.NORMAL
    return g


def test_heuristic_zero_at_same_point():
    assert heuristic((3, 4), (3, 4)) == 0.0


def test_heuristic_manhattan():
    assert heuristic((0, 0), (3, 4)) == 7.0


def test_astar_straight_path():
    grid = make_clean_grid()
    path = astar(grid, (0, 0), (0, 5))
    assert path is not None
    assert path[-1] == (0, 5)
    assert len(path) == 5


def test_astar_same_start_goal():
    grid = make_clean_grid()
    path = astar(grid, (5, 5), (5, 5))
    assert path == []


def test_astar_blocked_no_path():
    grid = make_clean_grid()
    # Build a wall
    for r in range(10):
        grid.cells[r][3].state = CellState.BLOCKED
    path = astar(grid, (0, 0), (0, 9))
    assert path is None


def test_astar_navigates_around_obstacle():
    grid = make_clean_grid()
    grid.cells[5][5].state = CellState.BLOCKED
    path = astar(grid, (5, 4), (5, 6))
    assert path is not None
    assert (5, 5) not in path
