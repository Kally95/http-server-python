import socket
import threading
import sys
from pathlib import Path

HTTP_200 = "HTTP/1.1 200 OK\r\n"
HTTP_404 = "HTTP/1.1 404 Not Found\r\n\r\n"
NOT_FOUND_RESPONSE = HTTP_404.encode()

def parse_http_request(request_text: str):
    lines = request_text.split("\r\n")
    request_line = lines[0]
    headers = {}
    for line in lines[1:]:
        if line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                key, value = parts
                headers[key.strip()] = value.strip()
    return request_line, headers

def handle_client(conn, addr, folder: Path = None):
    with conn:
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                decoded_data = data.decode('utf-8', errors='replace')
                if "\r\n\r\n" not in decoded_data:
                    continue

                header_text, body = decoded_data.split("\r\n\r\n", 1)
                request_line, headers = parse_http_request(header_text)

                try:
                    method, target, _ = request_line.split(" ")
                    print(target)
                except ValueError:
                    conn.sendall(NOT_FOUND_RESPONSE)
                    break

                if target == "/":
                    response = f"{HTTP_200}\r\n".encode()
                elif target.startswith("/echo/"):
                    value = target.split("/echo/", 1)[1]
                    response = (
                        f"{HTTP_200}"
                        f"Content-Type: text/plain\r\n"
                        f"Content-Length: {len(value)}\r\n\r\n"
                        f"{value}"
                    ).encode()
                elif target == "/user-agent":
                    user_agent = headers.get("User-Agent", "Unknown")
                    response = (
                        f"{HTTP_200}"
                        f"Content-Type: text/plain\r\n"
                        f"Content-Length: {len(user_agent)}\r\n\r\n"
                        f"{user_agent}"
                    ).encode()
                elif target.startswith("/files/") and method == "GET":
                    if folder is None:
                        response = NOT_FOUND_RESPONSE
                    else:
                        # Sanitize the file name to avoid directory traversal issues
                        file_name = Path(target[len("/files/"):]).name
                        abs_path = folder / file_name
                        file_contents = retrieve_file_contents(abs_path)
                        if file_contents is None:
                            response = NOT_FOUND_RESPONSE
                        else:
                            response = (
                                f"{HTTP_200}"
                                f"Content-Type: application/octet-stream\r\n"
                                f"Content-Length: {len(file_contents)}\r\n\r\n"
                            ).encode() + file_contents
                elif target.startswith("/files/") and method == "POST":
                    file_name = Path(target[len("/files/"):]).name
                    abs_path = folder / file_name
                    with open(abs_path, 'w') as f:
                        f.write(body)
                    response = HTTP_200.encode()
                else:
                    response = NOT_FOUND_RESPONSE

                conn.sendall(response)
        except Exception as e:
            print(f"Error handling client {addr}: {e}")

def retrieve_file_contents(file_path: Path):
    if not file_path.exists() or not file_path.is_file():
        print("File doesn't exist:", file_path)
        return None
    try:
        with file_path.open("rb") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def main():
    folder = None
    if len(sys.argv) > 1:
        folder = Path(sys.argv[2]).absolute()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 4221))
        s.listen()
        print("Server is listening on port 4221...")
        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            threading.Thread(target=handle_client, args=(conn, addr, folder)).start()

if __name__ == "__main__":
    main()
