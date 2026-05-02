from environment.grid import DisasterGrid
from environment.disaster_generator import DisasterGenerator
from environment.communication_map import CommunicationMap
from drones.swarm_controller import SwarmController
from algorithms.genetic.ga_optimizer import GAOptimizer
from simulation.metrics_tracker import MetricsTracker
from simulation.event_manager import EventManager
from config.settings import NUM_DRONES, EVENT_INTERVAL_TICKS, GRID_ROWS, GRID_COLS
import logging

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Central simulation engine. Orchestrates:
    - Grid environment
    - Disaster events
    - GA strategic planning (runs at start and every N ticks)
    - Swarm drone ticks
    - Metrics collection
    """

    def __init__(self):
        self.grid = DisasterGrid(GRID_ROWS, GRID_COLS)
        self.tick_count = 0
        self.running = False
        self.paused = False
        self.comm_map = CommunicationMap(self.grid)
        self.disaster_gen = DisasterGenerator(self.grid)
        self._rebuild_runtime_state()
        self._run_initial_ga()

    def _rebuild_runtime_state(self):
        """Recreate drone fleet and runtime trackers for the current grid."""
        self.swarm = SwarmController(self.grid, self.comm_map)
        self.metrics = MetricsTracker(self.grid, self.swarm)
        self.event_manager = EventManager()

    def _run_initial_ga(self):
        """Run GA at startup to assign zones."""
        logger.info("Running initial Genetic Algorithm optimization...")
        ga = GAOptimizer(self.grid, NUM_DRONES)
        assignment = ga.run()
        self.swarm.apply_zone_assignments(assignment, ga.zones)
        logger.info(f"GA completed. Zone assignments: {assignment}")

    def tick(self) -> dict:
        """
        Execute one simulation tick. Returns snapshot dict for GUI/API.
        """
        if not self.running or self.paused:
            return self._snapshot()

        self.tick_count += 1

        # Dynamic disaster events
        if self.tick_count % EVENT_INTERVAL_TICKS == 0:
            event = self.disaster_gen.generate_event(self.tick_count)
            self.event_manager.push(event)
            # Re-run GA periodically to adapt to new environment
            ga = GAOptimizer(self.grid, NUM_DRONES)
            assignment = ga.run()
            self.swarm.apply_zone_assignments(assignment, ga.zones)
            # Recompute comm map
            self.comm_map.recompute()

        # Tick all drones
        drone_events = self.swarm.tick(self.tick_count)
        for ev in drone_events:
            self.event_manager.push(ev)

        # Collect metrics
        self.metrics.record(self.tick_count)

        return self._snapshot()

    def _snapshot(self) -> dict:
        return {
            "tick": self.tick_count,
            "running": self.running,
            "paused": self.paused,
            "coverage": self.grid.coverage_rate(),
            "priority_coverage": self.grid.priority_coverage_rate(),
            "drones": [d.to_dict() for d in self.swarm.drones],
            "metrics": self.metrics.latest(),
            "recent_events": self.event_manager.recent(10),
        }

    def start(self):
        self.running = True
        self.paused = False

    def pause(self):
        self.paused = not self.paused

    def reset(self):
        """Reset drones and runtime state while preserving the current grid."""
        self.tick_count = 0
        self.running = False
        self.paused = False
        self._rebuild_runtime_state()
        self._run_initial_ga()

    def randomize_grid(self):
        """Create a brand-new randomized grid and rebuild all runtime state."""
        self.grid = DisasterGrid(GRID_ROWS, GRID_COLS)
        self.comm_map = CommunicationMap(self.grid)
        self.disaster_gen = DisasterGenerator(self.grid)
        self.tick_count = 0
        self.running = False
        self.paused = False
        self._rebuild_runtime_state()
        self._run_initial_ga()
