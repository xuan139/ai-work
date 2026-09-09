from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        connections = self._connections.get(user_id)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self._connections.pop(user_id, None)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        stale: list[tuple[int, WebSocket]] = []
        for user_id, connections in self._connections.items():
            for websocket in list(connections):
                try:
                    await websocket.send_json(payload)
                except RuntimeError:
                    stale.append((user_id, websocket))
        for user_id, websocket in stale:
            self.disconnect(user_id, websocket)


manager = ConnectionManager()
