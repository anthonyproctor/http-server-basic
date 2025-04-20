import socket
import threading

HOST = '0.0.0.0'
PORT = 4221

def handle_connection(conn, addr):
    with conn:
        request = conn.recv(1024).decode()
        print(f"[{addr}] Received request:\n{request}")

        request_line = request.splitlines()[0]
        parts = request_line.split(" ")
        if len(parts) < 2:
            response = "HTTP/1.1 400 Bad Request\r\n\r\n"
            conn.sendall(response.encode())
            return

        method, path = parts[0], parts[1]

        # Parse headers
        headers = {}
        for line in request.splitlines()[1:]:
            if line == "":
                break
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()

        # Routing
        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            echoed_string = path[len("/echo/"):]
            body = echoed_string
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(body)}\r\n"
                "\r\n"
                f"{body}"
            )
        elif path == "/user-agent":
            user_agent = headers.get("user-agent", "")
            body = user_agent
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(body)}\r\n"
                "\r\n"
                f"{body}"
            )
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        conn.sendall(response.encode())

# Main server loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Listening on http://{HOST}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_connection, args=(conn, addr))
        thread.start()
