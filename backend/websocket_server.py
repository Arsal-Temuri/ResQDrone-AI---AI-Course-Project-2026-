import asyncio
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from backend.api import app

logger = logging.getLogger(__name__)
_engine = None
_connected_clients = set()


def set_engine(engine):
    global _engine
    _engine = engine


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    _connected_clients.add(websocket)
    logger.info(f"WebSocket client connected. Total: {len(_connected_clients)}")
    try:
        while True:
            # Send state every second
            if _engine:
                state = _engine._snapshot()
                # Convert to JSON-safe dict
                await websocket.send_text(
                    json.dumps(
                        {
                            "tick": state["tick"],
                            "coverage": state["coverage"],
                            "drones": state["drones"],
                            "recent_events": state["recent_events"],
                        }
                    )
                )
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        _connected_clients.discard(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        _connected_clients.discard(websocket)
