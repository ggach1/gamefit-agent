"""표준 라이브러리 기반 HTTP/JSON 서버."""

from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .agent import GameJobAgent
from .job_fetch import fetch_job


ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = ROOT / "web"
AGENT = GameJobAgent()


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "GameFitAgent/1.0"

    def _json(self, data: object, status: int = HTTPStatus.OK) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/health":
            self._json({"status": "ok", "agent": "GameFit Agent"})
            return
        if path == "/api/tools":
            self._json({"tools": AGENT.list_tools()})
            return

        filename = "index.html" if path == "/" else path.lstrip("/")
        target = (WEB_ROOT / filename).resolve()
        if WEB_ROOT.resolve() not in target.parents and target != WEB_ROOT.resolve():
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = target.read_bytes()
        mime = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{mime}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/api/analyze":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > 200_000:
                raise ValueError("입력 크기는 200KB 이하여야 합니다.")
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError('JSON 객체가 필요합니다.')
            if not all(isinstance(body.get(k, ''), str) for k in ('job_url','job_posting','candidate_profile')):
                raise ValueError('입력은 문자열이어야 합니다.')
            if not body.get('candidate_profile', '').strip():
                raise ValueError('나의 기술·경험을 입력하세요.')
            source = fetch_job(body['job_url'].strip()) if body.get('job_url', '').strip() else None
            if source:
                body['job_posting'] = source['text']
            result = AGENT.analyze(
                str(body.get("job_posting", "")),
                str(body.get("candidate_profile", "")),
            )
            result['source'] = source
            self._json(result)
        except (ValueError, json.JSONDecodeError) as error:
            self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[GameFit] {self.address_string()} - {fmt % args}")


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), RequestHandler)
    print(f"GameFit Agent 서버 실행: http://{host}:{port}")
    print("종료: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
    finally:
        server.server_close()
