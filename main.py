"""
Entry point: Launches FastAPI backend in a background thread,
then starts the PyQt6 GUI application.
"""

import sys
import threading
import logging
import uvicorn
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from simulation.engine import SimulationEngine
from gui.main_window import MainWindow
from gui.audio_manager import AudioManager
import backend.api as api_module
import backend.websocket_server as ws_module
from config.settings import API_HOST, API_PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_backend(engine: SimulationEngine):
    """Run FastAPI server in background thread."""
    api_module.set_engine(engine)
    ws_module.set_engine(engine)

    from backend.api import app as fastapi_app
    from backend.websocket_server import websocket_endpoint  # registers WS route

    config = uvicorn.Config(
        app=fastapi_app,
        host=API_HOST,
        port=API_PORT,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    server.run()


def main():
    # Create the simulation engine (shared between GUI and API)
    engine = SimulationEngine()

    # Launch FastAPI backend in background thread
    api_thread = threading.Thread(target=run_backend, args=(engine,), daemon=True)
    api_thread.start()
    logger.info(f"Backend API started at http://{API_HOST}:{API_PORT}/docs")

    # Launch PyQt6 GUI with shared engine
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("Multi-Drone Disaster Response")

    audio_manager = AudioManager(qt_app)
    qt_app.installEventFilter(audio_manager)

    window = MainWindow(engine)
    window.show()

    QTimer.singleShot(0, audio_manager.play_theme)

    logger.info("GUI started. Ready.")
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
