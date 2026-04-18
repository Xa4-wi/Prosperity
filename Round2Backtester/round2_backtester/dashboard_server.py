from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .dashboard_data import build_run_payload, collect_runs


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "dashboard"
INDEX_HTML = DASHBOARD_DIR / "index.html"
DEFAULT_OUTPUT_ROOT = ROOT / "output"


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, output_root: Path, **kwargs: Any) -> None:
        self.output_root = output_root.resolve()
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/runs":
            self._json_response({"runs": collect_runs(self.output_root)})
            return
        if parsed.path == "/api/run":
            query = parse_qs(parsed.query)
            run_name = query.get("name", [""])[0]
            child_name = query.get("child", [""])[0] or None
            try:
                payload = build_run_payload(self.output_root, run_name, child=child_name)
            except FileNotFoundError:
                self.send_error(404, "Run not found")
                return
            self._json_response(payload)
            return
        if parsed.path in {"/", "/index.html"}:
            self._serve_file(INDEX_HTML)
            return
        super().do_GET()

    def _serve_file(self, path: Path) -> None:
        body = path.read_bytes()
        content_type, _ = mimetypes.guess_type(str(path))
        self.send_response(200)
        self.send_header("Content-Type", content_type or "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_response(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the Round 2 dashboard UI.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT, help="Directory containing saved run folders.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8022, help="Port to bind.")
    return parser.parse_args()


def serve_dashboard(output_root: Path, host: str = "127.0.0.1", port: int = 8022) -> None:
    output_root = output_root.resolve()
    if not output_root.exists():
        raise SystemExit(f"Output root not found: {output_root}")

    def handler(*handler_args: Any, **handler_kwargs: Any) -> DashboardHandler:
        return DashboardHandler(*handler_args, output_root=output_root, **handler_kwargs)

    server = ThreadingHTTPServer((host, port), handler)
    print(f"Round 2 dashboard running at http://{host}:{port} for {output_root}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    args = parse_args()
    serve_dashboard(args.output_root, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
