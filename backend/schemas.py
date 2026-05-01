from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class DroneInfo(BaseModel):
    drone_id: int
    row: int
    col: int
    battery: float
    status: str
    cells_visited: int
    distance_traveled: float
    comm_strength: float
    current_target: Optional[List[int]]
    replan_count: int
    total_reward: float


class CellInfo(BaseModel):
    row: int
    col: int
    state: str
    visited: bool
    visit_count: int
    comm_strength: float


class MetricsSnapshot(BaseModel):
    tick: int
    coverage: float
    priority_coverage: float
    avg_battery: float
    avg_reward: float
    avg_epsilon: float
    total_distance: float
    total_cells_visited: int


class GridState(BaseModel):
    tick: int
    running: bool
    paused: bool
    coverage: float
    priority_coverage: float
    drones: List[DroneInfo]
    metrics: Dict[str, Any]
