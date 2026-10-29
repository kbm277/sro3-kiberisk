#!/usr/bin/env python3
"""Пятый контейнер: проверяет остальные сервисы стека по сети Compose."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
import urllib.request

CHECKS = (
    ("site", "http", "site", 80, "/"),
    ("custom", "http", "custom", 8081, "/health"),
    ("cache", "redis", "cache", 6379, ""),
    ("db", "tcp", "db", 5432, ""),
)


def check_http(host: str, port: int, path: str) -> str:
    with urllib.request.urlopen(f"http://{host}:{port}{path}", timeout=2) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
    return "ok"


def check_tcp(host: str, port: int) -> str:
    with socket.create_connection((host, port), timeout=2):
        return "ok"


def check_redis(host: str, port: int) -> str:
    with socket.create_connection((host, port), timeout=2) as sock:
        sock.sendall(b"*1\r\n$4\r\nPING\r\n")
        reply = sock.recv(32)
    if b"+PONG" not in reply:
        raise RuntimeError(reply.decode("utf-8", "replace"))
    return "ok"


def probe(name: str, kind: str, host: str, port: int, path: str) -> dict:
    try:
        if kind == "http":
            detail = check_http(host, port, path)
        elif kind == "redis":
            detail = check_redis(host, port)
        else:
            detail = check_tcp(host, port)
        return {"name": name, "status": detail}
    except Exception as exc:
        return {"name": name, "status": "down", "error": str(exc)}


def snapshot() -> list:
    return [probe(*item) for item in CHECKS]


PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Мониторинг · Киберриск</title>
  <style>
    body { margin: 0; font-family: "Segoe UI", system-ui, sans-serif;
           background: #10141c; color: #e7eef6; }
    main { max-width: 720px; margin: 0 auto; padding: 36px 20px 48px; }
    h1 { margin-bottom: 4px; }
    p.note { color: #9aafc2; }
    .pill { display: inline-block; border: 1px solid #2a5f8a; color: #8ec8f0;
            border-radius: 999px; padding: 2px 10px; font-size: 0.8rem; }
    table { width: 100%; border-collapse: collapse; margin-top: 18px; }
    th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid #243244; }
    th { color: #9aafc2; font-weight: 600; }
    .ok { color: #3ddc97; }
    .down { color: #f07178; }
    a { color: #8ec8f0; }
  </style>
</head>
<body>
  <main>
    <span class="pill">свой образ · monitor</span>
    <h1>Мониторинг стека</h1>
    <p class="note">Этот контейнер ходит к остальным по именам сервисов Compose:
       site, custom, cache, db. Сам он пятый.</p>
    <table>
      <thead><tr><th>Сервис</th><th>Статус</th></tr></thead>
      <tbody>__ROWS__</tbody>
    </table>
    <p class="note">JSON: <a href="/api/status">/api/status</a></p>
  </main>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        rows = snapshot()
        if self.path == "/api/status":
            body = json.dumps({"service": "cyberrisk-monitor", "checks": rows}, ensure_ascii=False).encode()
            self._send(200, body, "application/json; charset=utf-8")
            return
        if self.path == "/health":
            self._send(200, b'{"status":"ok"}', "application/json")
            return
        if self.path in ("/", "/index.html"):
            html_rows = "".join(
                '<tr><td>{name}</td><td class="{css}">{status}</td></tr>'.format(
                    css="ok" if item["status"] == "ok" else "down",
                    **item,
                )
                for item in rows
            )
            page = PAGE.replace("__ROWS__", html_rows).encode()
            self._send(200, page, "text/html; charset=utf-8")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        print("%s - %s" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8082), Handler)
    print("cyberrisk-monitor listening on :8082")
    server.serve_forever()
