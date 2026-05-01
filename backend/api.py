from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import GridState, MetricsSnapshot
from typing import List
import logging

logger = logging.getLogger(__name__)

# Engine reference — set from main.py after creation
_engine = None

app = FastAPI(
    title="Multi-Drone Disaster Response API",
    description="REST + WebSocket API for the drone simulation system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def set_engine(engine):
    global _engine
    _engine = engine


@app.get("/", tags=["Health"])
def root():
    return {"status": "online", "service": "multi-drone-disaster-api"}


@app.get("/state", response_model=GridState, tags=["Simulation"])
def get_state():
    if not _engine:
        raise HTTPException(503, "Engine not initialized")
    return _engine._snapshot()


@app.post("/start", tags=["Simulation"])
def start_sim():
    if not _engine:
        raise HTTPException(503, "Engine not initialized")
    _engine.start()
    return {"status": "started"}


@app.post("/pause", tags=["Simulation"])
def pause_sim():
    if not _engine:
        raise HTTPException(503, "Engine not initialized")
    _engine.pause()
    return {"status": "paused" if _engine.paused else "resumed"}


@app.post("/reset", tags=["Simulation"])
def reset_sim():
    if not _engine:
        raise HTTPException(503, "Engine not initialized")
    _engine.reset()
    return {"status": "reset"}


@app.get("/metrics", tags=["Analytics"])
def get_metrics():
    if not _engine:
        raise HTTPException(503, "Engine not initialized")
    return {
        "coverage_series": _engine.metrics.get_series("coverage"),
        "priority_series": _engine.metrics.get_series("priority_coverage"),
        "battery_series": _engine.metrics.get_series("avg_battery"),
        "reward_series": _engine.metrics.get_series("avg_reward"),
        "epsilon_series": _engine.metrics.get_series("avg_epsilon"),
    }


@app.get("/drones", tags=["Drones"])
def get_drones():
    if not _engine:
        raise HTTPException(503, "Engine not initialized")
    return {"drones": [d.to_dict() for d in _engine.swarm.drones]}


@app.get("/events", tags=["Events"])
def get_events():
    if not _engine:
        raise HTTPException(503, "Engine not initialized")
    return {"events": _engine.event_manager.all()}


@app.get("/grid", tags=["Grid"])
def get_grid():
    if not _engine:
        raise HTTPException(503, "Engine not initialized")
    grid_data = []
    for row in _engine.grid.cells:
        row_data = []
        for cell in row:
            row_data.append(
                {
                    "row": cell.row,
                    "col": cell.col,
                    "state": cell.state.name,
                    "visited": cell.visited,
                    "comm_strength": round(cell.comm_strength, 2),
                }
            )
        grid_data.append(row_data)
    return {"grid": grid_data, "tick": _engine.tick_count}
