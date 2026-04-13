# ausbau/server.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ausbau.game_session import GameSession

app = FastAPI()

_BASE = os.path.dirname(os.path.abspath(__file__))
_HTML5 = os.path.join(_BASE, "html5")

app.mount("/static", StaticFiles(directory=_HTML5), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(_HTML5, "game.html"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = GameSession(end_game=1000)
    try:
        await session.run(websocket)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        # Log and close gracefully on unexpected errors
        print(f"Session error: {exc}")
        try:
            await websocket.close()
        except Exception:
            pass
