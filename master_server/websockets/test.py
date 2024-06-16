from fastapi import WebSocket
from master_server.utils.connection_manager import ConnectionManager
from master_server.utils.logging import AppLogger

class TestWebsocketConnectionManager(ConnectionManager):
    pass

manager = TestWebsocketConnectionManager()

logger = AppLogger().get_logger()

async def transcription_websocket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "type1":
                await websocket.send_json({
                    'result': "type1"
                })
               
    except Exception as e:
        logger.error(f"Error: {e}")
        manager.disconnect(websocket)