# 🟢 Matrix Chat App

A real-time encrypted chat application with a **Matrix-inspired** terminal aesthetic. Built with Python, it features a **FastAPI WebSocket server** for message relay and a **Tkinter GUI client** with AES-256-GCM end-to-end encryption.

![Python](https://img.shields.io/badge/Python-3.8%2B-green?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-WebSocket-009688?style=flat-square&logo=fastapi&logoColor=white)
![Encryption](https://img.shields.io/badge/Encryption-AES--256--GCM-critical?style=flat-square&logo=letsencrypt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

---

## ✨ Features

- **End-to-End Encryption** — All messages are encrypted with **AES-256-GCM** using a shared secret key. The server only relays opaque ciphertext.
- **Real-Time Messaging** — Powered by WebSockets for instant, bidirectional communication.
- **Matrix-Themed UI** — Black background with green monospace text, inspired by the iconic Matrix digital rain aesthetic.
- **Multi-Client Support** — Multiple users can connect simultaneously; messages are broadcast to all connected clients.
- **Color-Coded Messages** — Your own messages appear in green; other users' messages appear in purple for easy distinction.
- **Timestamps** — Every message displays the time it was received.
- **Standalone Executable** — Includes a PyInstaller spec for building a distributable Windows executable.

---

## 🏗️ Architecture

```
┌──────────────┐   WebSocket (JSON)   ┌──────────────────┐   WebSocket (JSON)   ┌──────────────┐
│   Client A   │ ◄──────────────────► │   FastAPI Server  │ ◄──────────────────► │   Client B   │
│  (Tkinter)   │                      │   (Broadcast)     │                      │  (Tkinter)   │
│              │                      │                   │                      │              │
│  AES Encrypt │                      │  Relay encrypted  │                      │  AES Decrypt │
│  AES Decrypt │                      │  payloads only    │                      │  AES Encrypt │
└──────────────┘                      └──────────────────┘                      └──────────────┘
```

### How It Works

1. **Server** (`server.py`) — A FastAPI application that accepts WebSocket connections on `/ws`. It maintains a set of connected clients and broadcasts every incoming message to all participants. The server **never decrypts** message content.

2. **Client** (`client.py`) — A Tkinter GUI application that connects to the server via WebSocket. On startup, the user provides a **username** and a **shared secret key**. Messages are encrypted before sending and decrypted upon receipt using AES-256-GCM.

3. **Message Flow**:
   - User types a message → client encrypts it with AES-256-GCM using a random 12-byte IV
   - Encrypted payload (IV + ciphertext + sender name) is sent as JSON over WebSocket
   - Server broadcasts the raw JSON to all connected clients
   - Each client decrypts the message using the shared key and displays it

---

## 📁 Project Structure

```
matrix_chat_app/
├── server.py          # FastAPI WebSocket server (message relay/broadcast)
├── client.py          # Tkinter GUI chat client (polished version with Send button)
├── main.py            # Earlier/simpler version of the chat client
├── client.spec        # PyInstaller spec file for building a standalone .exe
└── build/             # PyInstaller build artifacts
    └── client/        # Intermediate build files
```

| File | Description |
|------|-------------|
| [`server.py`](server.py) | WebSocket server using FastAPI. Accepts connections, tracks clients, and broadcasts messages. |
| [`client.py`](client.py) | Full-featured chat client with styled UI, Send button, color-coded messages, and AES-256-GCM encryption. |
| [`main.py`](main.py) | Minimal/prototype version of the client using `ScrolledText` widget. |
| [`client.spec`](client.spec) | PyInstaller configuration for packaging the client into a standalone Windows executable. |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/matrix_chat_app.git
   cd matrix_chat_app
   ```

2. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn websockets cryptography
   ```

### Running the Application

#### Step 1 — Start the Server

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

The server will start listening for WebSocket connections on `ws://localhost:8000/ws`.

#### Step 2 — Launch the Client(s)

Open one or more terminal windows and run:

```bash
python client.py
```

Each client will prompt you for:
1. **Username** — Your display name in the chat
2. **Shared Secret Key** — The encryption key (all participants must use the **same key** to read each other's messages)

> 💡 **Tip**: Open multiple client instances to simulate a group chat. All clients sharing the same secret key can communicate seamlessly.

---

## 🔐 Encryption Details

| Property | Value |
|----------|-------|
| **Algorithm** | AES-256-GCM (Galois/Counter Mode) |
| **Key Size** | 256 bits (32 bytes) |
| **IV/Nonce** | 12 bytes, randomly generated per message |
| **Library** | [`cryptography`](https://cryptography.io/) (`hazmat.primitives.ciphers.aead.AESGCM`) |

### Key Handling

- The user-provided secret key is encoded to bytes, then **padded or truncated** to exactly 32 bytes
- Padding uses null bytes (`\0`) if the key is shorter than 32 characters
- The same key must be shared out-of-band between all participants

### Message Format (JSON over WebSocket)

```json
{
  "from": "alice",
  "encrypted": [72, 101, 108, ...],
  "iv": [12, 34, 56, ...]
}
```

- `from` — Sender's username (plaintext)
- `encrypted` — AES-256-GCM ciphertext as a byte array
- `iv` — 12-byte initialization vector as a byte array

> ⚠️ **Security Note**: The `from` field is sent in plaintext and is not authenticated. In a production system, you would sign messages or include the sender identity in the authenticated encryption's associated data (AAD).

---

## 📦 Building a Standalone Executable

You can package the client as a standalone `.exe` using [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller client.spec
```

The executable will be generated in the `dist/` directory. The spec file is configured to:
- Build a **single-file** executable
- **Hide the console window** (GUI-only)
- Apply **UPX compression** for smaller file size

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Server | [FastAPI](https://fastapi.tiangolo.com/) + WebSockets |
| Client GUI | [Tkinter](https://docs.python.org/3/library/tkinter.html) (Python standard library) |
| WebSocket Client | [websockets](https://websockets.readthedocs.io/) |
| Encryption | [cryptography](https://cryptography.io/) (AES-256-GCM) |
| Packaging | [PyInstaller](https://pyinstaller.org/) |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  <i>Wake up, Neo... The Matrix has you.</i>
</p>
