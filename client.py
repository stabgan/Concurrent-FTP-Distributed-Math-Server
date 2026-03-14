"""
Client for the Concurrent FTP & Distributed Math Server

Connects to the server and provides an interactive menu:
  1. Perform a remote math operation
  2. Upload a file to the server
  3. Download a file from the server
  4. Quit
"""

import os
import socket
import struct

HOST = "localhost"
PORT = 12348
BUFFER_SIZE = 4096
HEADER_FMT = "!Q"  # must match server
HEADER_SIZE = struct.calcsize(HEADER_FMT)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _connect() -> socket.socket:
    """Create a new TCP connection to the server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    return sock


def math_operation() -> None:
    """Send a math expression to the server and print the result."""
    sock = _connect()
    try:
        sock.sendall(b"1")
        expr = input("Enter mathematical expression (e.g. 3+4): ").strip()
        sock.sendall(expr.encode())
        result = sock.recv(BUFFER_SIZE).decode()
        print(f"Result: {result}")
    except (ConnectionError, OSError) as exc:
        print(f"Error: {exc}")
    finally:
        sock.close()


def send_file() -> None:
    """Upload a file to the server."""
    fname = input("Enter filename to send: ").strip()
    fpath = os.path.join(BASE_DIR, fname) if not os.path.isabs(fname) else fname

    if not os.path.isfile(fpath):
        print(f"File not found: {fpath}")
        return

    file_size = os.path.getsize(fpath)
    sock = _connect()
    try:
        sock.sendall(b"2")
        # Send file-size header, then file data
        sock.sendall(struct.pack(HEADER_FMT, file_size))
        sent = 0
        with open(fpath, "rb") as f:
            while sent < file_size:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                sock.sendall(chunk)
                sent += len(chunk)
        # Wait for server acknowledgement
        ack = sock.recv(BUFFER_SIZE).decode()
        print(f"Server response: {ack}")
    except (ConnectionError, OSError) as exc:
        print(f"Error: {exc}")
    finally:
        sock.close()


def receive_file() -> None:
    """Download a file from the server."""
    sock = _connect()
    try:
        sock.sendall(b"3")
        # Read file-size header
        header = _recv_exact(sock, HEADER_SIZE)
        file_size = struct.unpack(HEADER_FMT, header)[0]

        if file_size == 0:
            print("Server has no file to send.")
            return

        save_path = os.path.join(BASE_DIR, "server2client.txt")
        received = 0
        with open(save_path, "wb") as f:
            while received < file_size:
                chunk = sock.recv(min(BUFFER_SIZE, file_size - received))
                if not chunk:
                    raise ConnectionError("Connection lost during file transfer")
                f.write(chunk)
                received += len(chunk)

        print(f"File saved to {save_path} ({received} bytes)")
    except (ConnectionError, OSError) as exc:
        print(f"Error: {exc}")
    finally:
        sock.close()


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    """Receive exactly *size* bytes from *sock*."""
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection closed while receiving data")
        data += chunk
    return data


MENU = """
--- Concurrent FTP & Math Client ---
1. Mathematical operation
2. Send file to server
3. Receive file from server
4. Quit
"""


def main() -> None:
    """Interactive client menu."""
    while True:
        print(MENU)
        try:
            choice = input("Select option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if choice == "1":
            math_operation()
        elif choice == "2":
            send_file()
        elif choice == "3":
            receive_file()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please enter 1-4.")


if __name__ == "__main__":
    main()
