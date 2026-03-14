import socket


def connect():
    """Create and return a new socket connected to the server."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12348))
    return s


def math_operation():
    """Send a math expression to the server and print the result."""
    s = connect()
    try:
        s.sendall(b"1")
        expr = input("Enter mathematical expression (e.g. 3+5, 10*2, 2^8): ")
        s.sendall(expr.encode())
        result = s.recv(1024).decode()
        print(f"Result: {result}")
    finally:
        s.close()


def send_file():
    """Send a file to the server (client → server)."""
    s = connect()
    try:
        s.sendall(b"2")
        fname = input("Enter filename to send: ")
        try:
            with open(fname, "rb") as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    print("Sending...")
                    s.sendall(chunk)
            print("File sent successfully.")
        except FileNotFoundError:
            print(f"Error: File '{fname}' not found")
    finally:
        s.close()


def receive_file():
    """Receive a file from the server (server → client)."""
    s = connect()
    try:
        s.sendall(b"3")
        with open("server2client.txt", "wb") as f:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                f.write(data)
        print("File received successfully.")
    finally:
        s.close()


def main():
    menu = (
        "\n--- Menu ---\n"
        "1. Mathematical Operation\n"
        "2. Send File to Server\n"
        "3. Receive File from Server\n"
        "4. Quit\n"
        "----> "
    )

    while True:
        try:
            opt = int(input(menu))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if opt == 1:
            math_operation()
        elif opt == 2:
            send_file()
        elif opt == 3:
            receive_file()
        elif opt == 4:
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
