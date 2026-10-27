"""Serve a pasta do estudo (site-analise/) na raiz de http://127.0.0.1:8790, sem cache, como no
endereço publicado (analise-da-virada.pages.dev), para conferir a página antes de publicar.

    python -I scripts/site_local.py [PORTA]

Com PORTA, serve em outra porta (por exemplo, quando outra sessão já usa a 8790).
"""
import functools
import sys
import http.server
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "site-analise"


class SemCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8790
    servidor = http.server.ThreadingHTTPServer(
        ("127.0.0.1", porta), functools.partial(SemCache, directory=str(PASTA)))
    print(f"Servindo {PASTA} em http://127.0.0.1:{porta} (sem cache)")
    servidor.serve_forever()
