from typing import List, Dict
from environment.grid import DisasterGrid
from drones.swarm_controller import SwarmController


class MetricsTracker:

    def __init__(self, grid: DisasterGrid, swarm: SwarmController):
        self.grid = grid
        self.swarm = swarm
        self.history: List[Dict] = []

    def record(self, tick: int):
        total_battery = sum(d.battery for d in self.swarm.drones)
        avg_battery = total_battery / max(1, len(self.swarm.drones))
        avg_reward = sum(a.average_reward() for a in self.swarm.agents) / max(
            1, len(self.swarm.agents)
        )
        avg_epsilon = sum(a.epsilon for a in self.swarm.agents) / max(
            1, len(self.swarm.agents)
        )
        snapshot = {
            "tick": tick,
            "coverage": self.grid.coverage_rate(),
            "priority_coverage": self.grid.priority_coverage_rate(),
            "avg_battery": avg_battery,
            "avg_reward": avg_reward,
            "avg_epsilon": avg_epsilon,
            "total_distance": sum(d.distance_traveled for d in self.swarm.drones),
            "total_cells_visited": sum(d.cells_visited for d in self.swarm.drones),
        }
        self.history.append(snapshot)

    def latest(self) -> Dict:
        return self.history[-1] if self.history else {}

    def get_series(self, key: str) -> List[float]:
        return [h[key] for h in self.history if key in h]
