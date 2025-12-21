from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys
import socket
import os

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start=3000, end=9000):
    for port in range(start, end+1):
        if not is_port_in_use(port):
            return port
    return 0

project_path = sys.argv[1]
os.chdir(project_path)

port = find_available_port()
print(port, file=sys.stderr) # Pass to stderr so the caller can read it

httpd = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
httpd.serve_forever()
