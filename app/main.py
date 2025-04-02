import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")


    server_socket = socket.create_server(("localhost", 4221))
    conn, _ = server_socket.accept() 
    data = conn.recv(4096)
    res = data.decode("utf-8").split("/")[1].split(' ')[0]
    if(not res):
        conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
    
    else:
        conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    

if __name__ == "__main__":
    main()
