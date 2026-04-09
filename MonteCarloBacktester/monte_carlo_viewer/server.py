from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
INDEX_HTML = ROOT / "index.html"
DEFAULT_BACKTESTS_DIR = ROOT.parent / "backtests"


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def read_dashboard(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    if "overall" not in data or "meta" not in data:
        return None
    return data


def summary_from_dashboard(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    overall = data.get("overall", {})
    products = data.get("products", {})
    meta = data.get("meta", {})
    total = overall.get("totalPnl", {})
    emerald = overall.get("emeraldPnl", {})
    tomato = overall.get("tomatoPnl", {})

    return {
        "name": path.name,
        "stem": path.stem,
        "path": str(path),
        "mtimeMs": int(path.stat().st_mtime_ns // 1_000_000),
        "sizeBytes": int(path.stat().st_size),
        "algorithmPath": meta.get("algorithmPath"),
        "sessionCount": meta.get("sessionCount"),
        "sampleSessions": meta.get("sampleSessions"),
        "total": {
            "mean": safe_float(total.get("mean")),
            "std": safe_float(total.get("std")),
            "p05": safe_float(total.get("p05")),
            "p50": safe_float(total.get("p50")),
            "p95": safe_float(total.get("p95")),
            "min": safe_float(total.get("min")),
            "max": safe_float(total.get("max")),
            "positiveRate": safe_float(total.get("positiveRate")),
            "sharpeLike": safe_float(total.get("sharpeLike")),
            "meanConfidenceLow95": safe_float(total.get("meanConfidenceLow95")),
            "meanConfidenceHigh95": safe_float(total.get("meanConfidenceHigh95")),
        },
        "emerald": {
            "mean": safe_float(emerald.get("mean")),
            "std": safe_float(emerald.get("std")),
            "p05": safe_float(emerald.get("p05")),
            "p50": safe_float(emerald.get("p50")),
            "p95": safe_float(emerald.get("p95")),
        },
        "tomato": {
            "mean": safe_float(tomato.get("mean")),
            "std": safe_float(tomato.get("std")),
            "p05": safe_float(tomato.get("p05")),
            "p50": safe_float(tomato.get("p50")),
            "p95": safe_float(tomato.get("p95")),
        },
        "correlation": safe_float(overall.get("emeraldTomatoCorrelation")),
        "productNames": sorted(products.keys()),
    }


def collect_dashboards(backtests_dir: Path) -> list[dict[str, Any]]:
    dashboards: list[dict[str, Any]] = []
    for path in sorted(backtests_dir.glob("*.json")):
        data = read_dashboard(path)
        if data is None:
            continue
        dashboards.append(summary_from_dashboard(path, data))
    dashboards.sort(key=lambda item: item["mtimeMs"], reverse=True)
    return dashboards


def detailed_payload(backtests_dir: Path, filename: str) -> dict[str, Any] | None:
    path = (backtests_dir / filename).resolve()
    if path.parent != backtests_dir.resolve() or not path.is_file():
        return None
    data = read_dashboard(path)
    if data is None:
        return None
    return {
        "summary": summary_from_dashboard(path, data),
        "dashboard": data,
    }


class ViewerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, backtests_dir: Path, **kwargs: Any) -> None:
        self.backtests_dir = backtests_dir
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/tests":
            self._json_response({"tests": collect_dashboards(self.backtests_dir)})
            return
        if parsed.path == "/api/test":
            query = parse_qs(parsed.query)
            filename = query.get("name", [""])[0]
            payload = detailed_payload(self.backtests_dir, filename)
            if payload is None:
                self.send_error(404, "Dashboard not found")
                return
            self._json_response(payload)
            return
        if parsed.path == "/" or parsed.path == "/index.html":
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
    parser = argparse.ArgumentParser(
        description="Browse Monte Carlo dashboard results and compare saved tests.",
    )
    parser.add_argument(
        "--backtests-dir",
        type=Path,
        default=DEFAULT_BACKTESTS_DIR,
        help="Directory containing dashboard JSON files.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8012, help="Port to bind.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    backtests_dir = args.backtests_dir.resolve()
    if not backtests_dir.is_dir():
        raise SystemExit(f"Backtests directory not found: {backtests_dir}")

    def handler(*handler_args: Any, **handler_kwargs: Any) -> ViewerHandler:
        return ViewerHandler(*handler_args, backtests_dir=backtests_dir, **handler_kwargs)

    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(
        f"Monte Carlo viewer running at http://{args.host}:{args.port} "
        f"for {backtests_dir}"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
