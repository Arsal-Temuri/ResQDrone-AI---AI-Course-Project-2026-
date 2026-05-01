import random
from typing import List, Tuple, Dict
from deap import base, creator, tools, algorithms
from environment.grid import DisasterGrid
from environment.cell import CellState
from config.settings import (
    GA_POPULATION_SIZE,
    GA_GENERATIONS,
    GA_CROSSOVER_PROB,
    GA_MUTATION_PROB,
    GA_TOURNAMENT_SIZE,
    FITNESS_WEIGHT_COVERAGE,
    FITNESS_WEIGHT_PRIORITY,
    FITNESS_WEIGHT_EFFICIENCY,
    FITNESS_WEIGHT_RISK,
)

# DEAP setup — only create classes once
if not hasattr(creator, "FitnessMax"):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", list, fitness=creator.FitnessMax)


class GAOptimizer:
    """
    Genetic Algorithm for strategic drone-to-zone assignment.

    Chromosome: List of length num_drones, each value is a zone index (0..num_zones-1).
    Fitness: weighted combination of coverage, priority, efficiency, risk.
    """

    def __init__(self, grid: DisasterGrid, num_drones: int, num_zones: int = None):
        self.grid = grid
        self.num_drones = num_drones
        self.num_zones = num_zones or num_drones  # Default: one zone per drone
        self.zones: List[List[Tuple[int, int]]] = []
        self._partition_grid()

    def _partition_grid(self):
        """Divide grid into approximately equal rectangular zones."""
        import math

        cols_per_zone = math.ceil(self.grid.cols / self.num_zones)
        self.zones = []
        for z in range(self.num_zones):
            zone_cells = []
            for r in range(self.grid.rows):
                for c in range(
                    z * cols_per_zone, min((z + 1) * cols_per_zone, self.grid.cols)
                ):
                    cell = self.grid.cells[r][c]
                    if cell.state != CellState.BASE:
                        zone_cells.append((r, c))
            self.zones.append(zone_cells)

    def _evaluate(self, individual: List[int]) -> Tuple[float]:
        """
        Fitness = w1*coverage_score + w2*priority_score + w3*efficiency_score - w4*risk_score
        """
        # Count how many drones cover each zone
        zone_drone_counts = [0] * self.num_zones
        for zone_idx in individual:
            zone_drone_counts[zone_idx] += 1

        coverage_score = 0.0
        priority_score = 0.0
        risk_score = 0.0
        efficiency_score = 0.0

        for z, zone_cells in enumerate(self.zones):
            if not zone_cells:
                continue
            drones_here = zone_drone_counts[z]

            # Coverage: more unique zones covered = better
            if drones_here > 0:
                coverage_score += 1.0

            # Priority: count HP cells in zone
            hp_count = sum(
                1
                for (r, c) in zone_cells
                if self.grid.cells[r][c].state == CellState.HIGH_PRIORITY
            )
            priority_score += hp_count * (1.0 if drones_here > 0 else 0.0)

            # Efficiency: penalize over-assignment
            if drones_here > 1:
                efficiency_score -= (drones_here - 1) * 0.5

            # Risk: penalize zones with many blocked/comm-risk cells
            risky = sum(
                1
                for (r, c) in zone_cells
                if self.grid.cells[r][c].state
                in (CellState.BLOCKED, CellState.COMM_RISK)
            )
            risk_score += risky * 0.1

        fitness = (
            FITNESS_WEIGHT_COVERAGE * coverage_score
            + FITNESS_WEIGHT_PRIORITY * priority_score
            + FITNESS_WEIGHT_EFFICIENCY * efficiency_score
            - FITNESS_WEIGHT_RISK * risk_score
        )
        return (fitness,)

    def run(self) -> List[int]:
        """
        Run the GA and return the best chromosome (drone → zone assignments).
        Returns a list of length num_drones, each value is a zone index.
        """
        toolbox = base.Toolbox()
        toolbox.register("attr_zone", random.randint, 0, self.num_zones - 1)
        toolbox.register(
            "individual",
            tools.initRepeat,
            creator.Individual,
            toolbox.attr_zone,
            self.num_drones,
        )
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self._evaluate)
        toolbox.register("mate", tools.cxUniform, indpb=0.5)
        toolbox.register(
            "mutate", tools.mutUniformInt, low=0, up=self.num_zones - 1, indpb=0.3
        )
        toolbox.register("select", tools.selTournament, tournsize=GA_TOURNAMENT_SIZE)

        pop = toolbox.population(n=GA_POPULATION_SIZE)
        hof = tools.HallOfFame(1)

        algorithms.eaSimple(
            pop,
            toolbox,
            cxpb=GA_CROSSOVER_PROB,
            mutpb=GA_MUTATION_PROB,
            ngen=GA_GENERATIONS,
            halloffame=hof,
            verbose=False,
        )

        return list(hof[0])

    def get_zone_for_drone(
        self, assignment: List[int], drone_idx: int
    ) -> List[Tuple[int, int]]:
        """Return the list of cells assigned to a specific drone."""
        zone_idx = assignment[drone_idx]
        return self.zones[zone_idx]
