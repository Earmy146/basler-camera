"""
Local control server for the deflectometry pattern viewer.

Run this on the PC, then open viewer.html from the phone browser using either:
  http://<PC_LAN_IP>:8000/viewer.html

or, with Android USB + adb reverse:
  adb reverse tcp:8000 tcp:8000
  http://127.0.0.1:8000/viewer.html
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import argparse
from functools import partial
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse


N_TOTAL = 8
PATTERN_NAMES = [f"V{i}" for i in range(4)] + [f"H{i}" for i in range(4)]

state = {
    "idx": 0,
    "T": 40,
    "version": 0,
}


def _clamp_idx(value):
    return max(0, min(N_TOTAL - 1, int(value)))


def _json_response(handler, payload, status=200):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _state_payload():
    idx = state["idx"]
    return {
        "idx": idx,
        "name": PATTERN_NAMES[idx],
        "T": state["T"],
        "total": N_TOTAL,
        "version": state["version"],
    }


class ControlHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            _json_response(self, _state_payload())
            return

        if parsed.path == "/api/set":
            query = parse_qs(parsed.query)
            if "idx" in query:
                state["idx"] = _clamp_idx(query["idx"][0])
            if "T" in query:
                state["T"] = max(1, int(query["T"][0]))
            state["version"] += 1
            _json_response(self, _state_payload())
            return

        if parsed.path == "/api/next":
            state["idx"] = (state["idx"] + 1) % N_TOTAL
            state["version"] += 1
            _json_response(self, _state_payload())
            return

        return super().do_GET()

    def log_message(self, fmt, *args):
        if self.path.startswith("/api/state"):
            return
        super().log_message(fmt, *args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--T", type=int, default=40)
    args = parser.parse_args()

    state["T"] = args.T
    root = Path(__file__).resolve().parent
    handler = partial(ControlHandler, directory=str(root))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving {root}")
    print(f"Viewer URL: http://<PC_LAN_IP>:{args.port}/viewer.html")
    print("API: /api/set?idx=0..7&T=40")
    print("Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
