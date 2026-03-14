# Concurrent FTP & Distributed Math Server

A multithreaded TCP server that handles multiple clients simultaneously, offering remote math evaluation and bidirectional file transfer over sockets.

---

## 📐 Architecture

```
┌──────────┐         TCP :12348         ┌──────────────┐
│ Client 1 │ ◄──────────────────────► │              │
├──────────┤                            │   Threaded   │
│ Client 2 │ ◄──────────────────────► │    Server    │
├──────────┤                            │              │
│  . . .   │ ◄──────────────────────► │  (up to 7    │
├──────────┤                            │   backlog)   │
│ Client N │ ◄──────────────────────► │              │
└──────────┘                            └──────────────┘
```

Each client connection is handled in a dedicated thread. The server supports three modes per session:

| Mode | Direction | Description |
|------|-----------|-------------|
| Math | Client → Server → Client | Evaluate `+  -  *  /  ^` expressions |
| Upload | Client → Server | Transfer a file to the server |
| Download | Server → Client | Transfer a file from the server |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| 🐍 Language | Python 3 |
| 🔌 Networking | `socket` (TCP/IPv4) |
| 🧵 Concurrency | `threading` (one thread per client) |
| 📁 File I/O | Chunked binary read/write (1 KB blocks) |

---

## 📦 Dependencies

None — uses only the Python standard library.

---

## 🚀 How to Run

### 1. Start the server

```bash
python server.py
```

The server binds to `localhost:12348` and waits for connections.

### 2. Start one or more clients

```bash
python client.py
```

You'll see a menu:

```
--- Menu ---
1. Mathematical Operation
2. Send File to Server
3. Receive File from Server
4. Quit
---->
```

- **Option 1** — type an expression like `12+8` or `2^10` and get the result back.
- **Option 2** — enter a local filename to upload to the server (saved as `client2server.txt`).
- **Option 3** — the server operator is prompted for a filename; the file is sent to the client (saved as `server2client.txt`).

---

## ⚠️ Known Issues / Limitations

- The server listens only on `localhost` — not accessible from other machines without changing the bind address.
- `s.listen(7)` sets the connection backlog to 7; this is not a hard cap on concurrent clients but controls the pending-connection queue size.
- Option 3 (download) requires manual input on the server terminal to choose the file, which blocks that handler thread.
- Math evaluation supports only single-operator expressions (e.g. `3+5`). Chained expressions like `3+5*2` are not supported.
- File transfers overwrite the destination file without confirmation.

---

## 📄 License

See [LICENSE](LICENSE).
