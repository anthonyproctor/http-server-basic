import socket

HOST = '0.0.0.0'
PORT = 4221

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Listening on http://{HOST}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        with conn:
            request = conn.recv(1024).decode()
            print(f"Received request:\n{request}")

            request_line = request.splitlines()[0]  # e.g., "GET /echo/hello HTTP/1.1"
            parts = request_line.split(" ")

            if len(parts) >= 2:
                path = parts[1]

                if path == "/":
                    response = "HTTP/1.1 200 OK\r\n\r\n"
                elif path.startswith("/echo/"):
                    # Extract the dynamic part after /echo/
                    echoed_string = path[len("/echo/"):]
                    body = echoed_string
                    headers = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {len(body)}\r\n"
                        "\r\n"
                    )
                    response = headers + body
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"
            else:
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"

            conn.sendall(response.encode())
