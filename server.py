
import os
import socket
import http.server
import socketserver
import argparse
import sys
from urllib.parse import urlunparse

def get_lan_ip():
    """Try to detect a LAN IPv4 address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
            if ip and not ip.startswith("127."):
                return ip
        except Exception:
            pass
    return None

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stdout.write("%s - - [%s] %s\n" % (
            self.client_address[0],
            self.log_date_time_string(),
            format%args
        ))

def run_server(directory, port):
    os.chdir(directory)  # serve from script's directory
    handler = QuietHandler
    host = "0.0.0.0"

    try:
        with socketserver.ThreadingTCPServer((host, port), handler) as httpd:
            lan_ip = get_lan_ip()
            scheme = "http"
            local_url = f"{scheme}://localhost:{port}/"
            lan_url = f"{scheme}://{lan_ip}:{port}/" if lan_ip else None

            print("\nServing directory:", directory)
            print(f"Local access: {local_url}")
            if lan_url:
                print(f"LAN access:   {lan_url}")
            else:
                print("Could not detect LAN IP — machine may not be connected to a network.")
            print("Press Ctrl+C to stop.\n")

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
    except OSError as e:
        print(f"Failed to start server on port {port}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Host the script’s directory on the LAN.")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to serve on (default 8000)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    run_server(script_dir, args.port)
