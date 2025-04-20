import socket

HOST = '0.0.0.0'
PORT = 4221

# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Listening on http://{HOST}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            conn.recv(1024)  # We don't care what the request is yet
            response = b"HTTP/1.1 200 OK\r\n\r\n"
            conn.sendall(response)
