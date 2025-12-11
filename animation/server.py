#!/usr/bin/env python3
"""
Simple HTTP server for the animation project
Run with: python server.py
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"🚀 Server running at {url}")
        print(f"📁 Serving files from: {os.getcwd()}")
        print("Press Ctrl+C to stop the server")
        
        # Automatically open browser
        try:
            webbrowser.open(url)
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main()

