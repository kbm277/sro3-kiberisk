#!/usr/bin/env python3
"""Свой контейнер для СРО 3: короткий реестр киберрисков."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

RISKS = [
    {
        "asset": "Docker-образ",
        "threat": "В образ попал секрет из .env",
        "likelihood": 3,
        "impact": 5,
    },
    {
        "asset": "Открытый порт",
        "threat": "Сервис доступен шире, чем нужно",
        "likelihood": 2,
        "impact": 4,
    },
    {
        "asset": "Учётная запись Hub",
        "threat": "Слабый пароль на Docker Hub",
        "likelihood": 2,
        "impact": 5,
    },
]

for item in RISKS:
    item["score"] = item["likelihood"] * item["impact"]


def level(score: int) -> str:
    if score >= 12:
        return "высокий"
    if score >= 6:
        return "средний"
    return "низкий"


PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Свой контейнер · Киберриск</title>
  <style>
    body { margin: 0; font-family: "Segoe UI", system-ui, sans-serif;
           background: #10140f; color: #e8f0e4; }
    main { max-width: 760px; margin: 0 auto; padding: 36px 20px 48px; }
    h1 { margin-bottom: 4px; }
    p.note { color: #9aaf96; }
    .pill { display: inline-block; border: 1px solid #3d6b45; color: #8ee0a0;
            border-radius: 999px; padding: 2px 10px; font-size: 0.8rem; }
    table { width: 100%; border-collapse: collapse; margin-top: 18px; }
    th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid #2a3828; }
    th { color: #9aaf96; font-weight: 600; }
    a { color: #8ee0a0; }
  </style>
</head>
<body>
  <main>
    <span class="pill">свой образ · python</span>
    <h1>Кастомный сервис киберриска</h1>
    <p class="note">Этот контейнер собран из своего Dockerfile, без готового сайта.
       Балл = вероятность × ущерб (шкала 1–5).</p>
    <table>
      <thead>
        <tr><th>Актив</th><th>Угроза</th><th>Балл</th><th>Уровень</th></tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <p class="note">JSON той же таблицы: <a href="/api/risks">/api/risks</a></p>
  </main>
</body>
</html>
"""

PAGE_TEMPLATE = PAGE.replace("{rows}", "__ROWS__")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/api/risks":
            payload = [
                {**item, "level": level(item["score"])} for item in RISKS
            ]
            body = json.dumps({"service": "cyberrisk-custom", "risks": payload}, ensure_ascii=False).encode()
            self._send(200, body, "application/json; charset=utf-8")
            return
        if self.path in ("/", "/index.html"):
            rows = "".join(
                "<tr><td>{asset}</td><td>{threat}</td><td>{score}</td><td>{level}</td></tr>".format(
                    level=level(item["score"]), **item
                )
                for item in RISKS
            )
            self._send(200, PAGE_TEMPLATE.replace("__ROWS__", rows).encode(), "text/html; charset=utf-8")
            return
        if self.path == "/health":
            self._send(200, b'{"status":"ok"}', "application/json")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        print("%s - %s" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8081), Handler)
    print("cyberrisk-custom listening on :8081")
    server.serve_forever()
