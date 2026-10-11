"""Record a real walkthrough of LabLens for the demo video.

Drives the actual app (upload -> analyze -> results -> explanation -> trends) with
deliberate pauses, and records the viewport to a webm. No faked footage: every frame
is the running app.
"""
import os
import shutil

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:5091/"
SAMPLE = "/home/roni/Roni_workspace/lablens/samples/sample_report.png"
OUT_DIR = "/tmp/opencode/lablens_rec"
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"], executable_path="/usr/bin/google-chrome")
        ctx = b.new_context(viewport={"width": 760, "height": 1100},
                            record_video_dir=OUT_DIR,
                            record_video_size={"width": 760, "height": 1100})
        pg = ctx.new_page()
        pg.goto(URL, wait_until="networkidle")
        pg.wait_for_timeout(2600)                      # intro on the landing view

        pg.set_input_files("#file", SAMPLE)
        pg.wait_for_timeout(2200)                      # show the report preview
        pg.click("#go")
        pg.wait_for_timeout(1500)                      # spinner / "reading the report"
        pg.wait_for_selector("#out table", timeout=180000)
        pg.wait_for_timeout(3000)                      # results settle

        # walk down the abnormal results
        for _ in range(4):
            pg.mouse.wheel(0, 620)
            pg.wait_for_timeout(1500)

        # open one explanation to show the grounding
        try:
            pg.eval_on_selector("#out summary", "el => el.click()")
        except Exception:
            pass
        pg.wait_for_timeout(3500)
        for _ in range(3):
            pg.mouse.wheel(0, 700)
            pg.wait_for_timeout(1300)
        pg.wait_for_timeout(2500)

        path = pg.video.path()
        ctx.close()
        b.close()

    dst = "/home/roni/Roni_workspace/lablens/samples/demo_walkthrough.webm"
    shutil.copy2(path, dst)
    print("recorded:", dst)


if __name__ == "__main__":
    main()
