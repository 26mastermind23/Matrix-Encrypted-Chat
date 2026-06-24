import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

app = FastAPI()

connected_clients = set()

# Use the same key as client; for demo, 32 bytes of zero:
AES_KEY = AESGCM(b'\0' * 32)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            # Just broadcast received message to all clients
            # (In a real app you might decrypt here, verify, etc.)

            # For demo, just send message back to all connected clients
            await broadcast(msg)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def broadcast(message: str):
    to_remove = set()
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            to_remove.add(client)
    for client in to_remove:
        connected_clients.remove(client)
