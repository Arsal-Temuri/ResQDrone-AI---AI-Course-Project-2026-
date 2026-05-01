# ResQDrone AI: Intelligent Time Aware Multi-Drone Coordination System for Dynamic Disaster Response

A comprehensive **AI-powered multi-drone simulation system** combining PyQt6 GUI, FastAPI backend, and hybrid AI algorithms (A*, Genetic Algorithm, Q-Learning) for autonomous disaster response coordination.

## Features

✅ **Hybrid AI Architecture**
- **A* Pathfinding** — Real-time tactical navigation with disaster-aware cost functions
- **Genetic Algorithm** — Strategic mission optimization and zone assignment
- **Q-Learning** — Adaptive reinforcement learning for drone behavior improvement

✅ **PyQt6 GUI Dashboard**
- Live animated grid with drone positions, battery status, and paths
- Real-time drone fleet status table
- Multi-chart metrics visualization (coverage, battery, Q-learning rewards)
- Dynamic event log
- Interactive controls (start, pause, reset, speed adjustment)

✅ **FastAPI REST + WebSocket Backend**
- Real-time simulation state API
- Live metrics streaming via WebSocket
- Full control endpoints (start/pause/reset)
- Grid and drone data export

✅ **Dynamic Environment**
- Procedural disaster event generation (floods, fires, communication loss)
- Grid state transitions
- Communication signal strength modeling
- Battery management and recharging

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

The GUI will launch with the simulation engine. The FastAPI backend runs in a background thread.

### 3. Access the API

While the app is running, open your browser:
```
http://127.0.0.1:8000/docs
```

This opens the interactive Swagger UI with all REST endpoints.

## Project Structure

```
multi_drone_disaster/
├── config/              # Configuration constants
├── environment/         # Grid, cells, communication, disaster events
├── drones/              # Drone model, battery, swarm controller
├── algorithms/          # A*, GA, Q-Learning implementations
│   ├── astar/
│   ├── genetic/
│   └── reinforcement/
├── simulation/          # Simulation engine, metrics, events
├── gui/                 # PyQt6 GUI components
│   ├── main_window.py
│   ├── grid_canvas.py
│   ├── control_panel.py
│   ├── drone_panel.py
│   ├── metrics_panel.py
│   ├── event_log.py
│   └── styles.py
├── backend/             # FastAPI application
│   ├── api.py
│   ├── websocket_server.py
│   └── schemas.py
├── tests/               # Unit tests (pytest)
├── main.py              # Entry point
└── requirements.txt
```

## Configuration

Edit [config/settings.py](config/settings.py) to adjust:

- Grid dimensions and drone count
- Simulation tick speed
- Battery drain/recharge rates
- A* cost weights
- GA population size and mutation rates
- Q-Learning parameters (alpha, gamma, epsilon)
- Event frequency and probabilities

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/state` | Full simulation snapshot |
| POST | `/start` | Start simulation |
| POST | `/pause` | Pause/resume |
| POST | `/reset` | Reset to initial state |
| GET | `/metrics` | Time series metrics |
| GET | `/drones` | Fleet status |
| GET | `/grid` | Full grid cell states |
| GET | `/events` | Disaster events log |
| WS | `/ws` | Live WebSocket feed |

## GUI Controls

**Simulation Panel:**
- ▶ START — Begin simulation
- ⏸ PAUSE — Pause/resume
- ⟳ RESET — Reset to initial state

**Speed Control:**
- Slider to adjust tick interval (50ms–2000ms)

**Overlays:**
- Signal strength overlay — Visualize communication zones
- Show planned paths — Display drone path predictions

**Metrics Display:**
- Live coverage % and priority coverage %
- Fleet average battery level
- Coverage progress chart over time
- Average Q-Learning reward
- Fleet average battery trend

**Drone Table:**
- Real-time drone position, battery, status
- Cells visited counter
- Total accumulated reward
- Epsilon (ε) exploration parameter decay

## Algorithm Details

### A* Pathfinding
Disaster-aware cost function:
```
cost = DISTANCE + ENERGY_PENALTY + RISK_COST + COMM_PENALTY
```
- Routes drones around obstacles and dangerous zones
- Prioritizes energy efficiency when battery is low
- Penalizes communication dead zones

### Genetic Algorithm
Optimizes fleet assignment every 15 ticks:
```
Fitness = 0.4·Coverage + 0.3·Priority + 0.2·Efficiency - 0.1·Risk
```
- Assigns drones to zones
- Balances coverage vs. efficiency
- Adapts to changing environment

### Q-Learning
Each drone learns independently:
```
Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') − Q(s,a)]
```
- State: position + battery level + comm strength
- Actions: 4-directional movement + stay
- Rewards for visiting high-priority cells, maintaining communication
- Penalties for battery drain, blocked cells

## Running Tests

```bash
pytest tests/ -v
```

## Performance Notes

- **GA execution**: ~100–300ms per optimization cycle
- **Q-Learning convergence**: Visible improvement after 200–500 ticks
- **Watch ε parameter**: Decays from 1.0 → 0.05 as drones shift from exploration to exploitation

## Architecture Diagram

```
SimulationEngine (shared)
├── DisasterGrid (20×20)
├── SwarmController (5 drones)
│   ├── Drone ×5 (position, battery, path)
│   └── QLearningAgent ×5 (Q-tables, ε-greedy)
├── GAOptimizer (DEAP: zone assignment)
├── DisasterGenerator (random events)
└── MetricsTracker (coverage, battery, reward)

GUI (PyQt6 + threading)
├── GridCanvas (animated visualization)
├── ControlPanel (start/pause/reset)
├── DronePanel (fleet table)
├── MetricsPanel (PyQtGraph charts)
└── EventLog (event history)

Backend (FastAPI + Uvicorn, daemon thread)
├── REST Endpoints
├── WebSocket live feed
└── Pydantic schemas
```

## Thread Safety

GUI runs in the main thread, FastAPI backend runs in a daemon thread. Both access the shared `SimulationEngine` instance. For production use, add a `threading.Lock` around engine state access.

## Customization

### Add Custom Disaster Events
Edit [environment/disaster_generator.py](environment/disaster_generator.py) to add new event types.

### Tune GA Fitness Function
Modify `_evaluate()` in [algorithms/genetic/ga_optimizer.py](algorithms/genetic/ga_optimizer.py).

### Change Grid Rendering
Modify [gui/grid_canvas.py](gui/grid_canvas.py) cell colors and overlays in `CELL_COLORS` and `paintEvent()`.

## Future Enhancements

- Deep Q-Learning (DQN) with neural networks
- 3D drone movement
- Real satellite map integration
- Computer vision obstacle detection
- Hardware integration with real drones
- Distributed multi-agent learning

## License

Developed for educational and research purposes.

## Author Notes

This system demonstrates **hybrid AI integration** in a realistic, scalable autonomous swarm architecture suitable for modern disaster response research and implementation.
