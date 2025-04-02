import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")


    server_socket = socket.create_server(("localhost", 4221))
    conn, _ = server_socket.accept() 
    data = conn.recv(4096)
    res = data.decode("utf-8").split("/")[2].split(' ')[0]
    content_length = len(list(res))
    REQUESTED_ENDPOINT = data.decode("utf-8").split("/")[1]
    print(data.decode().split('\r\n'))
    print(res)
    lines = data.decode().split('\r\n')
    host_line = next((line for line in lines if line.lower().startswith("get")), None)
    REQUESTED_PATH = host_line.split(' ')[1]
    if(REQUESTED_ENDPOINT == "echo"):
        formatted_response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len}\r\n\r\n{res}".format(res=res, len=content_length)
        conn.sendall(formatted_response.encode("utf-8"))
    elif (REQUESTED_PATH ==  "/echo/{string}".format(string=res)):
        conn.sendall(b"HTTP/1.1 202 OK\r\n\r\n")
    else:
        conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

        
    

if __name__ == "__main__":
    main()
