from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

app = FastAPI()

# Permitir solicitudes de cualquier origen (opcional, para fines de desarrollo)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Estructura para almacenar conexiones de usuarios por sala
active_connections: Dict[str, List[WebSocket]] = {}

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()
    if room not in active_connections:
        active_connections[room] = []
    active_connections[room].append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Reenviar el mensaje a otros usuarios en la misma sala
            for connection in active_connections[room]:
                if connection != websocket:
                    await connection.send_text(data)
    except WebSocketDisconnect:
        active_connections[room].remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
