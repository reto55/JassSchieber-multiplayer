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
        # Clean client-drop — socket is already gone, nothing to send.
        pass
    except Exception as exc:
        # Per the schieber-protocol skill invariant §5 ("No silent failures;
        # server responds with `error` …"), a bare close on an unexpected
        # backend exception is a contract violation. Send one last-ditch
        # protocol-shaped error payload before closing. If that send itself
        # fails (e.g. the socket is already half-closed), swallow the
        # secondary failure — the client is already unreachable.
        print(f"[ws error] {exc!r}", file=sys.stderr)
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Interner Serverfehler. Bitte neu laden.",
            })
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
