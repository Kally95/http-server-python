import socket
with socket.create_connection(("localhost", 4221)) as client_socket:
    client_socket.sendall(b"GET /echo/abc HTTP/1.1\r\n")
    
