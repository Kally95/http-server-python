import socket
import threading
import sys
from pathlib import Path

def handle_client(conn, addr, folder=None):
    with conn:  
        while True:
            data = conn.recv(1024)
            if not data:
                break 
            decoded = data.decode()
            if "\r\n\r\n" not in decoded:
                continue  
            request, headers = data.decode().split("\r\n", 1)
            method, target = request.split(" ")[:2]
            print(folder)
            if not data:
                break
            if target == "/":
                response = b"HTTP/1.1 200 OK\r\n\r\n"
            elif target.startswith("/echo/"):
                value = target.split("/echo/")[1]
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}".encode()
            elif target == "/user-agent":
                user_agent = [string for string in data.decode().split("\r\n") if "User-Agent" in string][0].split(":")[1].strip()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
            elif target.startswith("/files/"):
                if folder == None:
                    response = b"HTTP/1.1 404 Not Found\r\n\r\n"
                else:
                    file_name = target[len("/files/"):]
                    abs_path = folder / file_name
                    file_contents = retrieve_file_contents(abs_path)
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_contents)}\r\n\r\n".encode() + file_contents.encode()
            else:
                response = b"HTTP/1.1 404 Not Found\r\n\r\n"
            conn.sendall(response)
            
def retrieve_file_contents(folder_path):
    if not folder_path.exists():
        print("File doesn't exist")
        return None
    with folder_path.open() as f:
        file_contents = f.read()
    return file_contents

def main():

    folder = Path(sys.argv[2])
    print(folder)
    if not folder.is_dir():
        print(f"{folder} is not a valid directory.")
        folder = None
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 4221))
        s.listen()
        while True:
            conn, addr = s.accept()
            print(f"connected by {addr}")
            t = threading.Thread(target=handle_client, args=(conn, addr, folder.absolute()))   
            t.start() 
            
if __name__ == "__main__":
    main()