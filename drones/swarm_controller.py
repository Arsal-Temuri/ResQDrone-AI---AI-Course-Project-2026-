from typing import List, Dict, Optional
from drones.drone import Drone, DroneStatus
from drones.battery_manager import BatteryManager
from environment.grid import DisasterGrid
from environment.cell import CellState
from environment.communication_map import CommunicationMap
from algorithms.astar.astar import astar, find_best_target
from algorithms.reinforcement.qlearning import QLearningAgent
from config.settings import NUM_DRONES, GRID_ROWS, GRID_COLS


class SwarmController:
    """
    Manages all drones: tick-by-tick movement, path execution,
    battery management, Q-Learning updates.
    """

    def __init__(self, grid: DisasterGrid, comm_map: CommunicationMap):
        self.grid = grid
        self.comm_map = comm_map
        self.drones: List[Drone] = []
        self.agents: List[QLearningAgent] = []
        self._spawn_drones()

    def _spawn_drones(self):
        base_positions = self.grid.get_base_positions()
        for i in range(NUM_DRONES):
            base_r, base_c = base_positions[i % len(base_positions)]
            drone = Drone(drone_id=i, row=base_r, col=base_c)
            self.drones.append(drone)
            self.agents.append(QLearningAgent(drone_id=i))

    def apply_zone_assignments(self, assignments: List[int], zones: list):
        """Apply GA zone assignments to drones."""
        from algorithms.genetic.ga_optimizer import GAOptimizer

        for i, drone in enumerate(self.drones):
            zone_idx = assignments[i]
            if zone_idx < len(zones):
                drone.assigned_zone = zones[zone_idx][:]

    def tick(self, tick_num: int) -> List[dict]:
        """
        Execute one simulation tick for all drones.
        Returns list of events that happened this tick.
        """
        events = []
        for i, drone in enumerate(self.drones):
            agent = self.agents[i]
            event = self._tick_drone(drone, agent, tick_num)
            if event:
                events.append(event)
            agent.decay_epsilon()
        return events

    def _tick_drone(
        self, drone: Drone, agent: QLearningAgent, tick_num: int
    ) -> Optional[dict]:
        comm = self.comm_map.get_signal(drone.row, drone.col)
        drone.comm_strength = comm

        # Charging at base
        if drone.status == DroneStatus.CHARGING:
            BatteryManager.recharge(drone)
            cell = self.grid.get_cell(drone.row, drone.col)
            if cell and cell.state == CellState.BASE and drone.battery >= 100.0:
                drone.status = DroneStatus.IDLE
            return None

        # Return to base if low battery
        if drone.is_low_battery() and drone.status != DroneStatus.RETURNING:
            drone.status = DroneStatus.RETURNING
            base = self.grid.nearest_base(drone.row, drone.col)
            path = astar(self.grid, drone.position(), base, drone.battery)
            drone.current_path = path or []
            drone.current_target = base
            drone.replan_count += 1

        # Execute path step
        if drone.current_path:
            next_pos = drone.current_path.pop(0)
            nr, nc = next_pos
            cell = self.grid.get_cell(nr, nc)

            if not cell or not cell.is_traversable():
                # Blocked — replan
                drone.current_path = []
                drone.replan_count += 1
                return {"type": "replan", "drone_id": drone.drone_id, "tick": tick_num}

            # Q-Learning: state before move
            prev_battery = drone.battery
            prev_state = agent.get_state(drone.row, drone.col, drone.battery, comm)

            # Move drone
            drone.row, drone.col = nr, nc
            drone.distance_traveled += 1.0
            BatteryManager.drain_move(drone, cell.risk_cost())
            new_comm = self.comm_map.get_signal(nr, nc)
            drone.comm_strength = new_comm

            # Mark cell visited
            if drone.status != DroneStatus.RETURNING:
                if cell.state not in (CellState.BLOCKED, CellState.BASE):
                    self.grid.mark_visited(nr, nc, tick_num)
                    drone.cells_visited += 1
                    drone.status = DroneStatus.SCANNING

            # Q-Learning: compute reward and update
            reward = agent.compute_reward(cell, drone.battery, prev_battery, new_comm)
            next_state = agent.get_state(nr, nc, drone.battery, new_comm)
            action_taken = 0  # Simplified: action already committed via A* path
            agent.update(prev_state, action_taken, reward, next_state)
            drone.total_reward += reward

            # Reached base while returning
            if drone.status == DroneStatus.RETURNING and cell.state == CellState.BASE:
                drone.status = DroneStatus.CHARGING
                return {
                    "type": "charging",
                    "drone_id": drone.drone_id,
                    "tick": tick_num,
                }

            return None

        # No path — find new target
        if drone.status not in (DroneStatus.RETURNING, DroneStatus.CHARGING):
            target = find_best_target(
                self.grid, drone.position(), drone.assigned_zone, drone.battery
            )
            if target:
                path = astar(self.grid, drone.position(), target, drone.battery)
                if path:
                    drone.current_path = path
                    drone.current_target = target
                    drone.status = DroneStatus.NAVIGATING
                else:
                    drone.status = DroneStatus.IDLE
            else:
                drone.status = DroneStatus.IDLE

        return None
