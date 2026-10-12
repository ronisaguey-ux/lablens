#!/usr/bin/env python3
"""Upload a video to YouTube as UNLISTED (reused for the LabLens submission).

Same proven Studio flow as trending-tt/scripts/yt_publish_unlisted.py — navigate to the
upload dialog (auto-opens), set the file via CDP (the input is hidden, Playwright's
set_input_files refuses it), fill metadata via JS, answer the made-for-kids question,
advance, pick Unlisted, publish. Unlisted, not public: nothing shows on the channel.

usage: lablens_yt.py <video> <title> <desc_file>
"""
import os
import re
import sys
import time

sys.path.insert(0, "/home/roni/Roni_workspace/trending-tt/scripts")
from browser import launch_chrome, connect

PORT = 9367
PROFILE = "/tmp/opencode/bsprof"
CH = "UCEYajMIs22LFYb9EU_APEZg"


def log(*a):
    print("[up]", *a, flush=True)


def main():
    video, title = sys.argv[1], sys.argv[2]
    desc = open(sys.argv[3]).read() if len(sys.argv) > 3 else ""
    proc = launch_chrome(PROFILE, PORT)
    try:
        pw, browser, ctx = connect(PORT)
        page = ctx.new_page()
        page.set_viewport_size({"width": 1500, "height": 950})
        page.goto(f"https://studio.youtube.com/channel/{CH}/videos/upload?d=ud",
                  wait_until="domcontentloaded", timeout=120000)
        for _ in range(30):
            if page.evaluate("()=>!!document.querySelector('ytcp-uploads-dialog input[type=file], input[type=file]')"):
                break
            time.sleep(1)
        time.sleep(3)
        log("url:", page.url)

        cdp = ctx.new_cdp_session(page)
        doc = cdp.send("DOM.getDocument", {"depth": -1})
        node = cdp.send("DOM.querySelector", {"nodeId": doc["root"]["nodeId"], "selector": "input[type=file]"})
        if not node.get("nodeId"):
            log("no file node"); return 2
        cdp.send("DOM.setFileInputFiles", {"files": [video], "nodeId": node["nodeId"]})
        log("file set")
        time.sleep(18)

        js = page.evaluate
        has_desc = "true" if desc else "false"   # JS boolean, never Python 'True'
        js(f"""()=>{{const b=document.querySelectorAll("ytcp-uploads-dialog div[contenteditable='true']");
          if(b[0]){{b[0].focus();b[0].innerText={title!r};b[0].dispatchEvent(new Event('input',{{bubbles:true}}));}}
          if(b[1]&&({has_desc})){{b[1].focus();b[1].innerText={desc!r};b[1].dispatchEvent(new Event('input',{{bubbles:true}}));}}}}""")
        time.sleep(2)
        js("""()=>{const r=document.querySelector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']");r&&r.click();}""")
        time.sleep(2)

        for i in range(4):
            ok = js("()=>{const b=document.querySelector('#next-button');return b&&!b.hasAttribute('disabled');}")
            if not ok:
                break
            js("()=>document.querySelector('#next-button').click()"); log("next", i + 1); time.sleep(4)

        got = js("""()=>{const r=document.querySelector("tp-yt-paper-radio-button[name='UNLISTED']");if(r){r.click();return true;}return false;}""")
        log("unlisted selected:", got); time.sleep(2)

        res = js("""()=>{const b=document.querySelector('#done-button');if(b){b.click();return 'done';}
          const p=[...document.querySelectorAll('ytcp-button,button')].find(x=>/^(publish|save)/i.test(x.innerText||''));if(p){p.click();return p.innerText;}return 'none';}""")
        log("publish:", res); time.sleep(14)

        html = page.content()
        ids = re.findall(r'"videoId":"([\w-]{11})"', html) + re.findall(r"/video/([\w-]{11})", html)
        vid = ids[0] if ids else None
        print("WATCH_URL=" + ("https://youtu.be/" + vid if vid else "(not found) " + page.url))
        return 0
    finally:
        try:
            pw.stop()
        except Exception:
            pass
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
