import http.server
import socketserver
import webbrowser
import os

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

# Change to the directory where this script is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = MyHTTPRequestHandler

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 50)
        print(f"Server is running at http://localhost:{PORT}")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Automatically open the browser
        webbrowser.open(f'http://localhost:{PORT}/index.html')
        
        httpd.serve_forever()
except OSError:
    print(f"Port {PORT} is already in use. Trying port {PORT + 1}...")
    PORT += 1
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 50)
        print(f"Server is running at http://localhost:{PORT}")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        webbrowser.open(f'http://localhost:{PORT}/index.html')
        httpd.serve_forever()

