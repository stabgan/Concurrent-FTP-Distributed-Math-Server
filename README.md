# Concurrent FTP & Distributed Math Server

A multi-threaded TCP server that handles concurrent client connections for remote math evaluation and bidirectional file transfer.

## What It Does

The server spawns a new thread for each incoming client, supporting up to 7 simultaneous connections. Each client can:

- **Math mode** -- send an arithmetic expression (`3+4`, `10/3`, `2^8`) and get the result back instantly
- **Upload mode** -- transfer a local file to the server
- **Download mode** -- pull a file from the server to the client

File transfers use a size-prefixed binary protocol (8-byte header) so both sides know exactly how many bytes to expect -- no hanging sockets.

## Architecture

```
+----------+  TCP   +---------------------------+
|  Client  +------->|  Server (port 12348)      |
+----------+        |  +-- Thread 1 (math)      |
+----------+  TCP   |  +-- Thread 2 (upload)    |
|  Client  +------->|  +-- Thread 3 (download)  |
+----------+        +---------------------------+
```

Each connection is one-shot: the client picks an operation, executes it, and disconnects. The client menu loops so you can perform multiple operations in sequence (each opens a fresh socket).

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.8+ |
| Networking | `socket` (TCP) |
| Concurrency | `threading` (one thread per client) |
| Protocol | `struct`-packed 8-byte file-size headers |

## Getting Started

No external dependencies -- only the Python standard library.

```bash
# 1. Start the server
python server.py

# 2. In another terminal, start a client
python client.py
```

The client presents an interactive menu:

```
--- Concurrent FTP & Math Client ---
1. Mathematical operation
2. Send file to server
3. Receive file from server
4. Quit
```

### Configuration

Both `server.py` and `client.py` define these constants at the top of the file:

| Constant | Default | Description |
|----------|---------|-------------|
| `HOST` | `localhost` | Server bind / connect address |
| `PORT` | `12348` | TCP port |
| `MAX_CLIENTS` | `7` | `listen()` backlog (server only) |
| `BUFFER_SIZE` | `4096` | Read/write chunk size |

## Known Issues

- Math expressions containing a negative first operand (e.g. `-3+4`) will be mis-parsed because `-` is treated as the operator. Wrap in parentheses or restructure the expression.
- The server saves all uploaded files to `client2server.txt`, overwriting previous uploads. A production version should accept a target filename from the client.
- No TLS/encryption -- all data travels in plaintext. Suitable for local/lab use only.

## License

[MIT](LICENSE)
