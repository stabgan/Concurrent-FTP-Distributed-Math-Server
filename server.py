import socket
import threading


def calc(expression):
    """Evaluate a simple math expression with +, -, *, /, ^ operators."""
    try:
        if '+' in expression:
            a, b = expression.split('+', 1)
            return float(a) + float(b)
        elif '-' in expression:
            a, b = expression.split('-', 1)
            return float(a) - float(b)
        elif '*' in expression:
            a, b = expression.split('*', 1)
            return float(a) * float(b)
        elif '/' in expression:
            a, b = expression.split('/', 1)
            if float(b) == 0:
                return "Error: Division by zero"
            return float(a) / float(b)
        elif '^' in expression:
            a, b = expression.split('^', 1)
            return float(a) ** float(b)
        else:
            return "Error: Unsupported operation"
    except (ValueError, ZeroDivisionError) as e:
        return f"Error: {e}"


def thread_func(conn, addr):
    """Handle a single client connection in its own thread."""
    print(f"Got connection from {addr}")
    try:
        opt = int(conn.recv(1024).decode().strip())
        print(f"Client {addr} selected option: {opt}")

        if opt == 1:
            # Math operation mode
            msg = conn.recv(1024).decode().strip()
            result = calc(msg)
            conn.sendall(str(result).encode())

        elif opt == 2:
            # Receive file from client
            with open("client2server.txt", "wb") as f:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    f.write(data)
            print(f"File received from {addr}")

        elif opt == 3:
            # Send file to client
            fname = input("Enter filename to send: ")
            try:
                with open(fname, "rb") as f:
                    while True:
                        chunk = f.read(1024)
                        if not chunk:
                            break
                        print("Sending...")
                        conn.sendall(chunk)
                print(f"File sent to {addr}")
            except FileNotFoundError:
                print(f"Error: File '{fname}' not found")

        else:
            print(f"Invalid option {opt} from {addr}")

    except (ConnectionResetError, BrokenPipeError) as e:
        print(f"Connection error with {addr}: {e}")
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection closed: {addr}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 12348))
    server.listen(7)
    print("Server listening on localhost:12348 ...")

    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=thread_func, args=(conn, addr))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
