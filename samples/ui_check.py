"""Drive the LabLens UI end to end like a user, and prove the render path works.

Uploads the sample report through the real file input, clicks Analyze, waits for the
result table, and reports what it can see. Also captures a screenshot for the demo.
"""
import json
import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:5091/"
SAMPLE = "/home/roni/Roni_workspace/lablens/samples/sample_report.png"
SHOT = "/home/roni/Roni_workspace/lablens/samples/ui_screenshot.png"


def main():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"], executable_path="/usr/bin/google-chrome")
        pg = b.new_page(viewport={"width": 900, "height": 1200})
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(URL, wait_until="networkidle")

        title = pg.title()
        print("title:", title)

        # upload through the actual input the page uses
        pg.set_input_files("#file", SAMPLE)
        pg.wait_for_function("document.getElementById('go').disabled === false", timeout=5000)
        print("file accepted, Analyze enabled:", not pg.is_disabled("#go"))

        pg.click("#go")
        # wait for the results table to appear (up to 3 min: vision call)
        pg.wait_for_selector("#out table", timeout=180000)
        pg.wait_for_timeout(800)

        rows = pg.eval_on_selector_all("#out table tbody tr", "els => els.length")
        badges = pg.eval_on_selector_all("#out .badge", "els => els.map(e => e.textContent)")
        chips = pg.eval_on_selector_all("#out .chip", "els => els.map(e => e.textContent)")
        explains = pg.eval_on_selector_all("#out summary", "els => els.length")
        print("table rows:", rows)
        print("badges:", {b_: badges.count(b_) for b_ in set(badges)})
        print("chips:", chips)
        print("explain toggles:", explains)

        # open one explanation to prove the detail renders
        if explains:
            pg.eval_on_selector("#out summary", "el => el.click()")
            pg.wait_for_timeout(200)
            exp = pg.eval_on_selector("#out .exp", "el => el.innerText.slice(0,160)")
            print("opened explanation:", exp.replace("\n", " ")[:150])

        pg.screenshot(path=SHOT, full_page=True)
        print("screenshot:", SHOT)
        b.close()

    if errors:
        print("JS ERRORS:", errors[:5])
        sys.exit(2)
    print("OK: no JS errors")


if __name__ == "__main__":
    main()
