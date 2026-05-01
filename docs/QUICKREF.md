# Quick Reference

## Install & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the application
python main.py

# 3. Open API docs (while running)
http://127.0.0.1:8000/docs
```

## GUI Controls

| Button | Function |
|--------|----------|
| ▶ START | Begin simulation |
| ⏸ PAUSE | Pause/resume simulation |
| ⟳ RESET | Reset to initial state |

## Configuration

Edit `config/settings.py`:

```python
GRID_ROWS = 20              # Grid height
GRID_COLS = 20              # Grid width
NUM_DRONES = 5              # Number of drones
TICK_INTERVAL_MS = 300      # Simulation speed
GA_GENERATIONS = 30         # GA optimization depth
QL_ALPHA = 0.1              # Q-Learning learning rate
EVENT_INTERVAL_TICKS = 15   # Disaster event frequency
```

## Key Metrics

- **Coverage %** — Cells visited / total cells
- **Priority Coverage %** — High-priority cells visited
- **Avg Battery** — Fleet average battery level
- **ε (epsilon)** — Q-Learning exploration rate (high = explore, low = exploit)
- **Reward** — Accumulated Q-Learning reward per drone

## API Endpoints

```bash
# Health check
curl http://127.0.0.1:8000/

# Get state
curl http://127.0.0.1:8000/state

# Control
curl -X POST http://127.0.0.1:8000/start
curl -X POST http://127.0.0.1:8000/pause
curl -X POST http://127.0.0.1:8000/reset

# Data
curl http://127.0.0.1:8000/drones
curl http://127.0.0.1:8000/metrics
curl http://127.0.0.1:8000/events
curl http://127.0.0.1:8000/grid
```

## Run Tests

```bash
pytest tests/ -v
```

## Grid Colors

| Color | Meaning |
|-------|---------|
| Dark gray | Normal cell |
| Orange | Affected zone |
| Red | High-priority rescue zone |
| Black | Blocked/obstacle |
| Purple | Communication risk |
| Green | Base/charging station |

## Drone Status

| Status | Meaning |
|--------|---------|
| IDLE | Waiting for task |
| SCANNING | Visiting cells in zone |
| NAVIGATING | Moving to target |
| RETURNING | Heading back to base |
| CHARGING | Refueling at base |

## AI Algorithms at a Glance

### A* Pathfinding
- Finds shortest safe routes
- Avoids obstacles and risky cells
- Considers battery level

### Genetic Algorithm
- Runs every 15 ticks
- Assigns drones to zones
- Optimizes coverage & efficiency
- Adapts to environment changes

### Q-Learning
- Each drone learns independently
- Updates 1000s of times per simulation
- ε decays from 1.0 → 0.05
- Learns to avoid bad actions, repeat good ones

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Window blank | Reduce `CELL_SIZE_PX` to 24 in config |
| Address in use | Change `API_PORT` in config |
| Drones not moving | Click ▶ START and wait for GA optimization |
| No events | Wait — events appear every 15+ ticks |

## Performance Tips

| Goal | Adjustment |
|------|------------|
| Smoother GUI | Increase `TICK_INTERVAL_MS` to 500–1000 |
| Faster learning | Decrease `QL_EPSILON_DECAY` to 0.99 |
| More drones | Increase `NUM_DRONES` to 8–10 |
| Bigger grid | Increase `GRID_ROWS` and `GRID_COLS` |
| Better optimization | Increase `GA_GENERATIONS` to 50 |

## File Locations

| What | Where |
|------|-------|
| Entry point | `main.py` |
| Settings | `config/settings.py` |
| Algorithms | `algorithms/` |
| GUI | `gui/main_window.py` |
| API | `backend/api.py` |
| Tests | `tests/*.py` |

## Default Values

- Grid: 20×20
- Drones: 5
- Bases: 4 (corners)
- Tick speed: 300ms
- GA runs: Every 15 ticks
- Q-Learning updates: Every drone move
- Max events stored: 200

## Success Indicators

✅ GUI window opens (2-3 seconds)
✅ Drones appear as colored circles
✅ Start button enables simulation
✅ Drones move and paths show
✅ Battery bars visible on drones
✅ Metrics update in real-time
✅ Events appear in log
✅ API responds at localhost:8000

---

**For detailed setup:** See [SETUP.md](SETUP.md)
**For full documentation:** See [README.md](README.md)
