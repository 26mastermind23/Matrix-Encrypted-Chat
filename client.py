import asyncio
import websockets
import tkinter as tk
from tkinter import ttk, simpledialog
from datetime import datetime
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class MatrixChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matrix Chat")
        self.root.configure(bg="black")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', foreground='#00ff00', background='black', font=('Courier', 10, 'bold'))
        style.map('TButton',
                  foreground=[('active', '#00ff00')],
                  background=[('active', '#003300')])

        # Text area for chat
        self.text_area = tk.Text(root, bg="black", fg="#00ff00", font=("Courier", 10), wrap=tk.WORD, state=tk.DISABLED,
                                 padx=10, pady=10, bd=0, highlightthickness=0)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True, side=tk.TOP)

        # Frame for entry + send button
        entry_frame = tk.Frame(root, bg="black")
        entry_frame.pack(padx=10, pady=(0, 10), fill=tk.X, side=tk.BOTTOM)

        self.entry = tk.Entry(entry_frame, bg="black", fg="#00ff00", insertbackground="#00ff00", font=("Courier", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.send_message)

        self.send_btn = ttk.Button(entry_frame, text="Send", command=lambda: self.send_message(None))
        self.send_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Ask username and key
        self.username = simpledialog.askstring("Username", "Enter your username:", parent=root)
        key_input = simpledialog.askstring("Secret Key", "Enter shared secret key:", parent=root, show='*')
        # Make sure key length is 32 bytes (pad or truncate)
        key_bytes = key_input.encode()[:32].ljust(32, b'\0')
        self.aes_key = AESGCM(key_bytes)

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
                encrypted = bytes(data["encrypted"])
                decrypted = self.aes_key.decrypt(iv, encrypted, None).decode()
                self.display_message(data["from"], decrypted)
            except Exception as e:
                self.display_message("System", f"[Decryption failed] {str(e)}")

    def display_message(self, sender, message):
        time_str = datetime.now().strftime('%H:%M')
        self.text_area.config(state=tk.NORMAL)

        # Decide color based on whether sender is self or other
        if sender == self.username:
            sender_color = '#00ff00'  # bright green (your own username)
            msg_color = '#00cc00'     # slightly darker green for message text
        else:
            sender_color = '#aa00ff'  # purple for others
            msg_color = '#bb33ff'     # lighter purple for messages

        self.text_area.insert(tk.END, f"{sender} [{time_str}]: ", ('sender',))
        self.text_area.insert(tk.END, f"{message}\n", ('msg',))

        # Tag configs with dynamic colors
        self.text_area.tag_config('sender', foreground=sender_color, font=("Courier", 10, "bold"))
        self.text_area.tag_config('msg', foreground=msg_color, font=("Courier", 12))

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
def run_asyncio_loop(root, loop):
    try:
        loop.run_until_complete(asyncio.sleep(0.1))
    except Exception as e:
        print(f"Asyncio loop error: {e}")
    root.after(100, run_asyncio_loop, root, loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixChatApp(root)
    root.after(100, run_asyncio_loop, root, app.loop)
    root.mainloop()

