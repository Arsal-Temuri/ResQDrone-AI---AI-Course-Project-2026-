# User Scenarios — Walkthroughs for the Simulation GUI

This document lists simple, step-by-step user scenarios that show what happens from app start to finish. Each scenario describes which panels change, what the user clicks, and which algorithms are active. Language is kept simple for quick understanding.

---

## Scenario 1 — First Run: Start and Observe (Basic)

Goal: Launch the app and watch drones begin their tasks.

Steps:
1. Run `python main.py`.
2. The application opens with the main window showing these panels:
   - Control panel (top-left): `Start`, `Pause`, `Reset`, speed slider.
   - Grid canvas (center): 20×20 grid rendered with colored cells.
   - Drone panel (right): table listing each drone and current status.
   - Metrics panel (bottom-right): charts for Coverage, Avg Battery, Reward.
   - Event log (bottom): chronological list of events.
3. Click the `▶ START` button.

What changes / runs:
- The `Start` button becomes disabled; `Pause` is enabled.
- The backend GA (Genetic Algorithm) runs an initial zone assignment (startup optimization).
- Drones receive their initial zone assignments.
- A* pathfinding runs on each drone when it needs to move to a target cell.
- Q-Learning begins logging updates for each drone (learning happens as drones act).
- Grid canvas animates drones moving; paths are drawn as dotted lines when active.
- Event log shows GA completion message and initial drone actions.

User-visible cues:
- Drone statuses change from `IDLE` → `NAVIGATING`/`SCANNING` in the Drone panel.
- Coverage% in the Metrics panel increases as cells are visited.
- Battery bars update under each drone row.

---

## Scenario 2 — Interacting: Pause, Inspect, Toggle Overlays

Goal: Pause the simulation, inspect a cell and enable overlays.

Steps:
1. While running, click `⏸ PAUSE`.
2. Move the mouse over the grid to see hover tooltips showing cell coordinates, type, and communication strength.
3. Click a cell to select it — a blue border highlights selection and an info tooltip appears.
4. Use legend panel or control toggles to enable `Signal Overlay` or `Show Paths`.
5. Click `▶ START` to resume.

What changes / runs:
- Simulation loop halts while paused; algorithms stop making decisions until resumed.
- GUI remains fully interactive for inspection (hover and click still work).
- When resumed, drones continue from the same state; A* will recalculate if the selected cell changed something (e.g., new obstacle).

User-visible cues:
- Pause toggles in the Control panel.
- Tooltip and selection borders in the Grid canvas.
- Overlays appear immediately when toggled (signal heatmap, paths).

---

## Scenario 3 — Algorithm Behavior: GA + A* + Q-Learning (What runs when)

Goal: Understand which algorithms are active and when they run.

Sequence and timing (typical):
- At startup: Genetic Algorithm runs once to partition zones and assign drones.
- Every N ticks (default `EVENT_INTERVAL_TICKS` / GA schedule): GA re-runs to re-optimize assignments if the environment changed.
- A* Pathfinding: runs per drone whenever a drone needs to navigate to a specific target cell. It is the low-latency tactical planner.
- Q-Learning: runs incrementally during the simulation as drones take actions. Each action results in Q-table updates and changes to `ε` (epsilon).

How this appears to the user:
- GA messages appear in the Event log: "GA completed — zone assignments: [...]".
- A* is usually invisible but visible when paths are toggled on (dotted lines appear).
- Q-Learning metrics (reward, epsilon) update in the Metrics panel and Drone panel (epsilon shown per drone row if enabled).

---

## Scenario 4 — Emergency: New High-Priority Event Appears

Goal: See how the system reacts to a sudden disaster event.

Steps:
1. While simulation runs, the disaster generator creates a high-priority event (e.g., `FIRE`) in the grid.
2. The affected cells change color to `RED`/`ORANGE` and appear in the Grid canvas.
3. The Event log posts the new event with coordinates and severity.

What changes / runs:
- The A* planners for nearby drones trigger immediate replanning to the new high-priority cells.
- GA may re-evaluate assignments at the next scheduled GA run to rebalance coverage.
- Q-Learning agents record reward signals when drones respond successfully or fail, slowly updating behavior.

User-visible cues:
- Grid cells flash or change color to indicate the new event.
- Drone icons change to `NAVIGATING` or `RETURNING` depending on battery and assigned policy.
- Event log shows the event and subsequent actions taken by drones.

---

## Scenario 5 — End-to-End Demo (Combined Scenario)

Goal: An easy demo script to show the whole system from start to a small mission complete.

Steps to run the demo:
1. Start the app: `python main.py`.
2. Click `▶ START` and wait ~3 seconds for the initial GA to complete.
3. Watch drones spread into zones and begin visiting cells.
4. After ~30–60 seconds, trigger one or two high-priority events (or wait for them to appear).
5. Observe A* replanning, drones responding, battery changes, and metrics evolving.
6. Optionally, `⏸ PAUSE` and inspect a drone's Q-table or selected cell to explain decisions.
7. Click `⟳ RESET` to return to the initial state and repeat.

What this demonstrates to a viewer:
- How strategic planning (GA) sets a high-level mission.
- How tactical planning (A*) executes individual movements.
- How adaptation (Q-Learning) refines behavior over time.
- How the GUI visualizes state, logs events, and displays metrics.

---

## Quick Glossary (for reading the panels)
- Control panel: start/pause/reset, speed slider, overlay toggles.
- Grid canvas: main visualization (cell colors, drones, paths, overlays).
- Drone panel: per-drone rows with `ID`, `Status`, `Battery`, `Assigned Zone`, `ε` (if shown).
- Metrics panel: charts (Coverage%, Avg Battery, Reward over time).
- Event log: textual timeline of GA runs, events, and system messages.

---

If you'd like, I can:
- Add short annotated screenshots for each scenario.
- Create a `DEMO.md` with a one-command script for an auto-play demo.

File location: `docs/scenario.md` (this file)
