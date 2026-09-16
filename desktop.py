"""Portable Windows launcher; no Python installation required after freezing."""
import argparse
import threading
import webbrowser
from http.server import ThreadingHTTPServer
from agent_server.server import RequestHandler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), RequestHandler)
    except OSError:
        # An existing server might be an old version: choose a free port, not a stale page.
        server = ThreadingHTTPServer(('127.0.0.1', 0), RequestHandler)
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'GameFit ready: {url}\nKeep this window open. Close it or press Ctrl+C to stop.', flush=True)
    if not args.no_browser:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
