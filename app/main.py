import socket
import threading
import os
import sys

# Parse optional --directory flag
files_dir = None
if "--directory" in sys.argv:
    dir_index = sys.argv.index("--directory") + 1
    if dir_index < len(sys.argv):
        files_dir = sys.argv[dir_index]

HOST = '0.0.0.0'
PORT = 4221

def handle_connection(conn, addr):
    with conn:
        request = conn.recv(4096).decode()
        print(f"[{addr}] Received request:\n{request}")

        lines = request.splitlines()
        if not lines:
            return

        request_line = lines[0]
        parts = request_line.split(" ")
        if len(parts) < 2:
            conn.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            return

        method, path = parts[0], parts[1]

        # Parse headers
        headers = {}
        i = 1
        while i < len(lines):
            line = lines[i]
            i += 1
            if line == "":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()

        # Handle Content-Length for request body (used in POST)
        content_length = int(headers.get("content-length", 0))

        # Read request body if needed
        body = ""
        if content_length > 0:
            # Get the raw bytes
            request_bytes = request.encode()
            header_end_index = request_bytes.find(b"\r\n\r\n") + 4
            body_bytes = request_bytes[header_end_index:]

            # If body not fully received, read the remaining
            while len(body_bytes) < content_length:
                body_bytes += conn.recv(content_length - len(body_bytes))

            body = body_bytes.decode()

        # Routing
        if path == "/":
            conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        elif path.startswith("/echo/"):
            echo = path[len("/echo/"):]
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(echo)}\r\n"
                "\r\n"
                f"{echo}"
            )
            conn.sendall(response.encode())
        elif path == "/user-agent":
            user_agent = headers.get("user-agent", "")
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(user_agent)}\r\n"
                "\r\n"
                f"{user_agent}"
            )
            conn.sendall(response.encode())
        elif path.startswith("/files/"):
            if not files_dir:
                conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
                return

            filename = path[len("/files/"):]
            filepath = os.path.join(files_dir, filename)

            if method == "GET":
                if os.path.isfile(filepath):
                    with open(filepath, "rb") as f:
                        file_data = f.read()
                    response_headers = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/octet-stream\r\n"
                        f"Content-Length: {len(file_data)}\r\n"
                        "\r\n"
                    )
                    conn.sendall(response_headers.encode() + file_data)
                else:
                    conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

            elif method == "POST":
                try:
                    with open(filepath, "w") as f:
                        f.write(body)
                    conn.sendall(b"HTTP/1.1 201 Created\r\n\r\n")
                except Exception as e:
                    print(f"Error writing file: {e}")
                    conn.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
            else:
                conn.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
        else:
            conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

# Start server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server running on http://{HOST}:{PORT}" + (f" — Serving from: {files_dir}" if files_dir else ""))

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_connection, args=(conn, addr)).start()
