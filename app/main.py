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

            # Get the first line of the request (the request line)
            request_line = request.splitlines()[0]

            # Example: "GET / HTTP/1.1"
            parts = request_line.split(" ")

            if len(parts) >= 2:
                path = parts[1]  # this is the request target

                if path == "/":
                    response = "HTTP/1.1 200 OK\r\n\r\n"
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"
            else:
                # Bad request (optional for now)
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"

            conn.sendall(response.encode())
