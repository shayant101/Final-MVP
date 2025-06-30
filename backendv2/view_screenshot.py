#!/usr/bin/env python3
"""
Simple web server to view screenshots
"""
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_screenshots():
    """Start a simple HTTP server to view screenshots"""
    
    # Change to screenshots directory
    screenshots_dir = Path("screenshots")
    if not screenshots_dir.exists():
        print("❌ Screenshots directory not found")
        return
    
    os.chdir(screenshots_dir)
    
    # Find the latest screenshot
    png_files = list(Path(".").glob("*.png"))
    if not png_files:
        print("❌ No screenshot files found")
        return
    
    latest_screenshot = max(png_files, key=os.path.getctime)
    print(f"📸 Latest screenshot: {latest_screenshot}")
    
    # Start HTTP server
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🌐 Serving screenshots at http://localhost:{PORT}")
            print(f"📱 View latest screenshot: http://localhost:{PORT}/{latest_screenshot}")
            print("Press Ctrl+C to stop the server")
            
            # Open browser automatically
            webbrowser.open(f"http://localhost:{PORT}/{latest_screenshot}")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    serve_screenshots()