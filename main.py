import asyncio
import websockets
import tkinter as tk
from tkinter import simpledialog, scrolledtext
from datetime import datetime
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class MatrixChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matrix Chat")
        self.root.configure(bg="black")

        self.text_area = scrolledtext.ScrolledText(root, bg="black", fg="#00ff00", font=("Courier", 10))
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)

        self.entry = tk.Entry(root, bg="black", fg="#00ff00", insertbackground="#00ff00")
        self.entry.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.entry.bind("<Return>", self.send_message)

        self.username = simpledialog.askstring("Username", "Enter your username:", parent=root)
        key_input = simpledialog.askstring("Secret Key", "Enter shared secret key:", parent=root, show='*')
        self.aes_key = AESGCM(key_input.ljust(32).encode())

        self.ws = None
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.connect())

    async def connect(self):
        uri = "ws://localhost:8000/ws"
        self.ws = await websockets.connect(uri)
        self.loop.create_task(self.receive())
    
    async def receive(self):
        while True:
            try:
                msg = await self.ws.recv()
                data = json.loads(msg)
                iv = bytes(data["iv"])
                decrypted = self.aes_key.decrypt(iv, bytes(data["encrypted"]), None).decode()
                self.display_message(data["from"], decrypted)
            except Exception as e:
                self.display_message("System", f"[Decryption failed] {str(e)}")

    def display_message(self, sender, message):
        time_str = datetime.now().strftime('%H:%M')
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, f"{sender} [{time_str}]: {message}\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

    def send_message(self, event):
        message = self.entry.get().strip()
        if message and self.ws:
            iv = os.urandom(12)
            encrypted = self.aes_key.encrypt(iv, message.encode(), None)
            data = {
                "from": self.username,
                "encrypted": list(encrypted),
                "iv": list(iv)
            }
            asyncio.ensure_future(self.ws.send(json.dumps(data)))
            self.entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixChatApp(root)
    asyncio.get_event_loop().run_forever()