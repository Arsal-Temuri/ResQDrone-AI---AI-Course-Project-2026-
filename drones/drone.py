from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple, Optional
from config.settings import BATTERY_MAX, LOW_BATTERY_THRESHOLD


class DroneStatus(Enum):
    IDLE = auto()
    SCANNING = auto()
    NAVIGATING = auto()
    RETURNING = auto()
    CHARGING = auto()
    COMM_RELAY = auto()


@dataclass
class Drone:
    drone_id: int
    row: int
    col: int
    battery: float = BATTERY_MAX
    status: DroneStatus = DroneStatus.IDLE
    assigned_zone: List[Tuple[int, int]] = field(default_factory=list)
    current_path: List[Tuple[int, int]] = field(default_factory=list)
    current_target: Optional[Tuple[int, int]] = None
    comm_strength: float = 1.0
    cells_visited: int = 0
    distance_traveled: float = 0.0
    replan_count: int = 0
    total_reward: float = 0.0

    def is_low_battery(self) -> bool:
        return self.battery <= LOW_BATTERY_THRESHOLD

    def position(self) -> Tuple[int, int]:
        return (self.row, self.col)

    def to_dict(self) -> dict:
        return {
            "drone_id": self.drone_id,
            "row": self.row,
            "col": self.col,
            "battery": round(self.battery, 1),
            "status": self.status.name,
            "cells_visited": self.cells_visited,
            "distance_traveled": round(self.distance_traveled, 1),
            "comm_strength": round(self.comm_strength, 2),
            "current_target": self.current_target,
            "replan_count": self.replan_count,
            "total_reward": round(self.total_reward, 1),
        }
