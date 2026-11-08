"""Open every generated page in headless Edge, report JS errors, and print each sheet to PDF + PNG.

    python make_sheets.py && python tools/check.py            # all sheets
    python tools/check.py dominion.html army.html               # only these

Output goes to tools/out/ (git-ignored): <name>.pdf (what the printer gets, A4) and <name>-<n>.png per page.
Look at the PNGs/PDF before calling a layout change done: a page that spills onto a second sheet of paper,
text overflowing a box, or numbers in the wrong order in Hebrew are the usual problems.
Needs `pip install playwright pymupdf` (Edge is used through channel="msedge", no browser download).
"""
import functools
import http.server
import pathlib
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "out"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main(names):
    OUT.mkdir(exist_ok=True)
    names = names or sorted(p.name for p in (ROOT / "sheets").glob("*.html"))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    bad = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        for name in ["../index.html"] + names:
            page = browser.new_page(viewport={"width": 1000, "height": 1400})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"{base}/sheets/{name}", wait_until="load")  # not networkidle: Google Fonts can hang it
            page.wait_for_timeout(600)
            stem = pathlib.Path(name).stem
            sheets = page.locator(".sheet")
            n = sheets.count()
            for k in range(n):
                sheets.nth(k).screenshot(path=str(OUT / f"{stem}-{k + 1}.png"))
            if n:
                page.pdf(path=str(OUT / f"{stem}.pdf"), prefer_css_page_size=True, print_background=True)
            else:
                page.screenshot(path=str(OUT / f"{stem}.png"), full_page=True)
            bad += bool(errors)
            print(f"{name:20} pages={n:2} errors={errors or 'none'}")
            page.close()
        browser.close()
    srv.shutdown()
    print(f"output in {OUT}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
