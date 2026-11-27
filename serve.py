#!/usr/bin/env python3
"""Tiny static dev server for this site:  python3 serve.py [port]   (default 8767)

Unlike `python3 -m http.server` it sends Cache-Control: no-store, so the browser never reuses a stale
wall.json / glimpse.js / face files after you regenerate or edit them.

Binds to 0.0.0.0 so the site also works behind a proxied preview host. Set HOST=127.0.0.1 to
keep it local-only. PORT can be used instead of the positional port argument.
"""
import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class NoCache(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def do_POST(self):
        # The intro/editor fire a best-effort "seen" beacon. A static host has no
        # backend for it, so acknowledge it locally instead of returning 501.
        if self.path.split("?")[0].endswith("/api/seen"):
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            super().do_POST()


host = os.environ.get("HOST", "0.0.0.0")
port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", "8767"))
handler = partial(NoCache, directory=str(ROOT))
httpd = ThreadingHTTPServer((host, port), handler)
print(f"serving http://localhost:{port}/  (no-cache, {host}:{port})  Ctrl+C to stop", flush=True)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
