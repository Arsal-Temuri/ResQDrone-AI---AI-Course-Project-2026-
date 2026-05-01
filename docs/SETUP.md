# Setup & Run Guide

## System Requirements

- **Python 3.11+**
- **Windows 10+, macOS, or Linux**
- 4GB RAM minimum (8GB recommended)
- Display resolution 1400×900 or higher

## Step-by-Step Installation

### Step 1: Create Python Virtual Environment (Recommended)

```bash
# Navigate to project root
cd multi_drone_disaster

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Installation time:** ~2–5 minutes depending on network speed

**Troubleshooting:**
- If `deap` installation fails on Windows, ensure you have a C++ compiler (Visual Studio Build Tools or MinGW)
- If `PyQt6` fails, try: `pip install PyQt6 --no-cache-dir`

### Step 3: Run the Application

```bash
python main.py
```

**Expected output:**
```
2026-05-01 12:34:56,789 [INFO] simulation.engine: Running initial Genetic Algorithm optimization...
2026-05-01 12:34:58,123 [INFO] simulation.engine: GA completed. Zone assignments: [0, 1, 2, 0, 1]
2026-05-01 12:34:58,456 [INFO] __main__: Backend API started at http://127.0.0.1:8000/docs
2026-05-01 12:34:58,789 [INFO] __main__: GUI started. Ready.
```

The PyQt6 window will open with the simulation dashboard.

## First Time Running

1. **GUI will appear** with a 20×20 grid showing:
   - Base stations (green) at corners
   - Affected zones (orange/brown)
   - High-priority zones (red)
   - Blocked areas (dark)
   - 5 colored drone circles

2. **Click ▶ START** to begin simulation

3. **Observe:**
   - Drones will navigate their assigned zones
   - Paths appear as dotted lines
   - Battery levels displayed below each drone
   - Coverage % increases as cells are visited
   - Metrics charts update in real-time

4. **Experiment with controls:**
   - **Speed slider** — Adjust tick interval (50ms–2000ms)
   - **Signal overlay** — Visualize communication zones
   - **Show paths** — Toggle path visualization

## Accessing the Backend API

While the GUI is running:

### Swagger UI (Interactive API Documentation)
Open browser: `http://127.0.0.1:8000/docs`

### REST API Examples

**Get current state:**
```bash
curl http://127.0.0.1:8000/state
```

**Start simulation:**
```bash
curl -X POST http://127.0.0.1:8000/start
```

**Get metrics:**
```bash
curl http://127.0.0.1:8000/metrics
```

**Get drone fleet:**
```bash
curl http://127.0.0.1:8000/drones
```

### WebSocket Client (Python Example)

```python
import asyncio
import websockets
import json

async def main():
    uri = "ws://127.0.0.1:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Tick {data['tick']}: Coverage {data['coverage']:.1%}")

asyncio.run(main())
```

## Running Unit Tests

```bash
# Install pytest if not already done
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_astar.py -v

# Run with coverage report
pip install pytest-cov
pytest tests/ --cov=algorithms --cov=environment --cov=drones -v
```

**Expected test count:** 13 tests across 3 modules

## Configuration Adjustments

Edit `config/settings.py` to customize:

```python
# Grid size
GRID_ROWS = 20
GRID_COLS = 20

# Drone count
NUM_DRONES = 5

# Simulation speed (ms per tick)
TICK_INTERVAL_MS = 300

# Battery parameters
BATTERY_MAX = 100.0
BATTERY_DRAIN_PER_MOVE = 2.0
LOW_BATTERY_THRESHOLD = 20.0

# Genetic Algorithm
GA_GENERATIONS = 30  # Increase for better optimization
GA_POPULATION_SIZE = 50

# Q-Learning
QL_ALPHA = 0.1  # Learning rate
QL_EPSILON_START = 1.0  # Exploration rate

# Event frequency
EVENT_INTERVAL_TICKS = 15  # Fewer ticks = more events
```

Save and restart the application for changes to take effect.

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'PyQt6'"
**Solution:**
```bash
pip install --upgrade PyQt6
```

### Issue: "ModuleNotFoundError: No module named 'deap'"
**Solution:**
```bash
pip install deap
# If that fails on Windows:
pip install deap --no-cache-dir
```

### Issue: GUI window appears blank or doesn't render
**Solution:**
- Ensure screen resolution is at least 1400×900
- Try reducing `CELL_SIZE_PX` in `config/settings.py` from 36 to 24
- Restart the application

### Issue: "Address already in use" (FastAPI port conflict)
**Solution:**
Change `API_PORT` in `config/settings.py`:
```python
API_PORT = 8001  # or any unused port
```

### Issue: Application crashes on reset
**Solution:**
This is normal behavior. DEAP sometimes retains creator state. The `hasattr` guard should handle it, but if it persists:
```python
# In simulation/engine.py, add after _run_initial_ga():
import gc
gc.collect()
```

### Issue: Drones aren't moving
**Solution:**
- Click ▶ START button
- Check that simulation is not paused (⏸ button)
- Verify drones have battery (green bars below circles)
- Wait for GA optimization to complete (~2 seconds on startup)

### Issue: No events in event log
**Solution:**
- Events only appear every 15 ticks (configurable in `config/settings.py`)
- Increase `NUM_DRONES` or increase `GRID_ROWS`/`GRID_COLS` to see more activity

## Performance Tuning

### For Smooth GUI (Higher FPS)
```python
TICK_INTERVAL_MS = 500  # Slower ticks
GA_GENERATIONS = 15    # Faster GA
```

### For Faster Simulation (More Science)
```python
TICK_INTERVAL_MS = 50   # Very fast ticks
GA_GENERATIONS = 30    # Better optimization
```

### For Better Q-Learning Convergence
```python
QL_EPSILON_START = 1.0
QL_EPSILON_DECAY = 0.99  # Slower decay
QL_ALPHA = 0.15         # Slightly higher learning rate
```

## Project Layout

```
multi_drone_disaster/
├── main.py                      ← Entry point
├── requirements.txt             ← Dependencies
├── README.md                    ← Full documentation
├── SETUP.md                     ← This file
│
├── config/
│   ├── __init__.py
│   └── settings.py              ← All constants
│
├── environment/                 ← Grid & world
│   ├── cell.py                  ← Cell states
│   ├── grid.py                  ← Grid class
│   ├── disaster_generator.py    ← Event generation
│   └── communication_map.py     ← Signal strength
│
├── drones/                      ← Autonomous agents
│   ├── drone.py                 ← Drone dataclass
│   ├── battery_manager.py       ← Power management
│   └── swarm_controller.py      ← Drone tick logic
│
├── algorithms/                  ← AI engines
│   ├── astar/
│   │   └── astar.py             ← Pathfinding
│   ├── genetic/
│   │   └── ga_optimizer.py      ← Zone assignment
│   └── reinforcement/
│       └── qlearning.py         ← Adaptive learning
│
├── simulation/                  ← Engine & tracking
│   ├── engine.py                ← Main loop
│   ├── metrics_tracker.py       ← Performance data
│   └── event_manager.py         ← Event history
│
├── gui/                         ← PyQt6 interface
│   ├── main_window.py           ← Main window
│   ├── grid_canvas.py           ← Animated grid
│   ├── control_panel.py         ← Controls
│   ├── drone_panel.py           ← Fleet table
│   ├── metrics_panel.py         ← Charts
│   ├── event_log.py             ← Event display
│   └── styles.py                ← Dark theme
│
├── backend/                     ← FastAPI server
│   ├── api.py                   ← REST endpoints
│   ├── websocket_server.py      ← WebSocket feed
│   └── schemas.py               ← Data models
│
└── tests/                       ← Unit tests
    ├── test_astar.py
    ├── test_ga.py
    └── test_qlearning.py
```

## Next Steps

1. **Explore the GUI:**
   - Start simulation and watch drones navigate
   - Observe Q-Learning epsilon (ε) decay in drone table
   - Monitor coverage % increase over time

2. **Test the API:**
   - Open http://127.0.0.1:8000/docs
   - Try `/drones` and `/metrics` endpoints
   - Write a simple WebSocket client

3. **Modify Parameters:**
   - Increase number of drones in `config/settings.py`
   - Change grid size for different disaster scales
   - Adjust GA crossover/mutation probabilities

4. **Run the Tests:**
   - Execute `pytest tests/ -v` to verify all algorithms work correctly

5. **Extend the System:**
   - Add new cell types to `environment/cell.py`
   - Implement custom reward functions in `algorithms/reinforcement/qlearning.py`
   - Design new disaster event types in `environment/disaster_generator.py`

## Debugging

### Enable Debug Logging

Add to `main.py` before launching:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
```

### Monitor Simulation State

Create a test script:
```python
from simulation.engine import SimulationEngine

engine = SimulationEngine()
engine.start()
for _ in range(10):
    state = engine.tick()
    print(f"Tick {state['tick']}: Coverage {state['coverage']:.1%}")
    print(f"  Drones: {[d['battery'] for d in state['drones']]}")
```

## Support

For issues:
1. Check the troubleshooting section above
2. Review the main [README.md](README.md)
3. Check error logs in terminal output
4. Verify Python version: `python --version`
5. Verify dependencies: `pip list | grep -E "PyQt|fastapi|numpy|deap"`

## Final Checklist

- [ ] Python 3.11+ installed (`python --version`)
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] No error messages on `python main.py`
- [ ] GUI window opens successfully
- [ ] ▶ START button works
- [ ] Drones move across grid
- [ ] Metrics charts update
- [ ] API accessible at `http://127.0.0.1:8000/docs`

**You're ready to go!** 🚀
