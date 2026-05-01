import heapq
from typing import List, Tuple, Optional, Dict
from environment.grid import DisasterGrid
from environment.cell import CellState
from config.settings import COST_DISTANCE, COST_ENERGY, COST_RISK_BLOCKED


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(
    grid: DisasterGrid,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    battery_level: float = 100.0,
) -> Optional[List[Tuple[int, int]]]:
    """
    Disaster-aware A* pathfinding.

    Cost function:
        f(n) = g(n) + h(n)
        g(n) = cumulative cost (distance + energy + risk + comm penalty)
        h(n) = Manhattan distance to goal

    Returns list of (row, col) tuples from start (exclusive) to goal (inclusive),
    or None if no path found.
    """
    if start == goal:
        return []

    open_heap: List[Tuple[float, Tuple[int, int]]] = []
    heapq.heappush(open_heap, (0.0, start))

    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    g_score: Dict[Tuple[int, int], float] = {start: 0.0}

    while open_heap:
        _, current = heapq.heappop(open_heap)

        if current == goal:
            # Reconstruct path
            path = []
            node = current
            while node != start:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path

        r, c = current
        for neighbor in grid.neighbors(r, c):
            nr, nc = neighbor.row, neighbor.col
            # Base movement cost
            move_cost = COST_DISTANCE
            # Energy cost proxy (drain per move, scaled by battery concern)
            if battery_level < 30.0:
                move_cost += COST_ENERGY * 2.0  # Penalize long paths when low battery
            else:
                move_cost += COST_ENERGY * 0.5
            # Cell-specific risk
            move_cost += neighbor.risk_cost()

            tentative_g = g_score[current] + move_cost

            if (nr, nc) not in g_score or tentative_g < g_score[(nr, nc)]:
                g_score[(nr, nc)] = tentative_g
                f = tentative_g + heuristic((nr, nc), goal)
                came_from[(nr, nc)] = current
                heapq.heappush(open_heap, (f, (nr, nc)))

    return None  # No path found


def find_best_target(
    grid: DisasterGrid,
    drone_pos: Tuple[int, int],
    assigned_zone: List[Tuple[int, int]],
    battery_level: float,
) -> Optional[Tuple[int, int]]:
    """
    Among cells in the assigned zone, find the highest-priority unvisited cell
    that A* can actually reach given current battery.
    """
    from environment.cell import CellState

    candidates = []
    for r, c in assigned_zone:
        cell = grid.get_cell(r, c)
        if cell and not cell.visited and cell.state != CellState.BLOCKED:
            priority = 0
            if cell.state == CellState.HIGH_PRIORITY:
                priority = 3
            elif cell.state == CellState.AFFECTED:
                priority = 2
            elif cell.state == CellState.COMM_RISK:
                priority = 1
            dist = abs(drone_pos[0] - r) + abs(drone_pos[1] - c)
            candidates.append(
                (-priority, dist, (r, c))
            )  # neg priority = max priority first

    candidates.sort()
    for _, dist, target in candidates:
        path = astar(grid, drone_pos, target, battery_level)
        if path is not None:
            return target
    return None
