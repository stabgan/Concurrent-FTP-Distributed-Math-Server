"""
Concurrent FTP & Distributed Math Server

A multi-threaded TCP server that handles:
  1. Remote mathematical operations (+, -, *, /, ^)
  2. Receiving files from clients (upload)
  3. Sending files to clients (download)
"""

import os
import socket
import struct
import threading

HOST = "localhost"
PORT = 12348
MAX_CLIENTS = 7
BUFFER_SIZE = 4096
HEADER_FMT = "!Q"  # unsigned 8-byte big-endian (file size header)
HEADER_SIZE = struct.calcsize(HEADER_FMT)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def calc(expression: str) -> str:
    """Evaluate a simple two-operand math expression.

    Supported operators (checked in order): +  -  *  /  ^
    Returns the string representation of the result, or an error message.
    """
    operators = [
        ("+", lambda a, b: a + b),
        ("-", lambda a, b: a - b),
        ("*", lambda a, b: a * b),
        ("/", lambda a, b: a / b),
        ("^", lambda a, b: a ** b),
    ]
    for symbol, func in operators:
        if symbol in expression:
            try:
                left, right = expression.split(symbol, 1)
                return str(func(float(left), float(right)))
            except (ValueError, ZeroDivisionError) as exc:
                return f"ERROR: {exc}"
    return "ERROR: unsupported expression"


def recv_exact(sock: socket.socket, size: int) -> bytes:
    """Receive exactly *size* bytes from *sock*, or raise ConnectionError."""
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection closed while receiving data")
        data += chunk
    return data


def handle_math(conn: socket.socket, addr: tuple) -> None:
    """Receive a math expression, compute, and send the result back."""
    raw = conn.recv(BUFFER_SIZE)
    if not raw:
        return
    expression = raw.decode().strip()
    print(f"  [{addr}] Math request: {expression}")
    result = calc(expression)
    conn.sendall(result.encode())
    print(f"  [{addr}] Result sent: {result}")


def handle_receive_file(conn: socket.socket, addr: tuple) -> None:
    """Receive a file from the client and save it on the server."""
    # 1. Read the 8-byte file-size header
    header = recv_exact(conn, HEADER_SIZE)
    file_size = struct.unpack(HEADER_FMT, header)[0]
    print(f"  [{addr}] Incoming file: {file_size} bytes")

    save_path = os.path.join(BASE_DIR, "client2server.txt")
    received = 0
    with open(save_path, "wb") as f:
        while received < file_size:
            chunk = conn.recv(min(BUFFER_SIZE, file_size - received))
            if not chunk:
                raise ConnectionError("Connection lost during file transfer")
            f.write(chunk)
            received += len(chunk)

    conn.sendall(b"OK")
    print(f"  [{addr}] File saved to {save_path}")


def handle_send_file(conn: socket.socket, addr: tuple) -> None:
    """Send a file from the server to the client."""
    send_path = os.path.join(BASE_DIR, "server2client.txt")
    if not os.path.isfile(send_path):
        # Send zero-length header to signal "no file"
        conn.sendall(struct.pack(HEADER_FMT, 0))
        print(f"  [{addr}] File not found: {send_path}")
        return

    file_size = os.path.getsize(send_path)
    conn.sendall(struct.pack(HEADER_FMT, file_size))

    sent = 0
    with open(send_path, "rb") as f:
        while sent < file_size:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            conn.sendall(chunk)
            sent += len(chunk)

    print(f"  [{addr}] Sent {sent} bytes")


def client_handler(conn: socket.socket, addr: tuple) -> None:
    """Handle a single client connection (runs in its own thread)."""
    print(f"[+] Connection from {addr}")
    try:
        raw_opt = conn.recv(BUFFER_SIZE)
        if not raw_opt:
            return
        opt = int(raw_opt.decode().strip())
        print(f"  [{addr}] Option selected: {opt}")

        if opt == 1:
            handle_math(conn, addr)
        elif opt == 2:
            handle_receive_file(conn, addr)
        elif opt == 3:
            handle_send_file(conn, addr)
        else:
            conn.sendall(b"ERROR: unknown option")
    except (ValueError, ConnectionError, OSError) as exc:
        print(f"  [{addr}] Error: {exc}")
    finally:
        conn.close()
        print(f"[-] Connection closed: {addr}")


def main() -> None:
    """Start the TCP server and accept connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)
    print(f"Server listening on {HOST}:{PORT} (max {MAX_CLIENTS} queued connections)")

    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=client_handler, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.close()


if __name__ == "__main__":
    main()
