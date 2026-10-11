"""Vision extraction: read a photo of a lab report into structured values.

The model does ONE job here - transcribe the numbers that are printed on the sheet.
It is explicitly told not to interpret, not to invent values it cannot read, and to
mark the sheet as not-a-lab-report when it is something else. Every later judgement
(flagging, explaining) happens in analyze.py against the knowledge base, so a
vision mistake cannot silently become a medical claim.
"""
import base64
import io
import json
import os
import re
import urllib.request

from PIL import Image

# Free local router first; it fans out to Gemini Flash (vision-capable).
ENDPOINT = os.environ.get("LLM_BASE_URL", "http://127.0.0.1:8790/v1/chat/completions")
MODEL = os.environ.get("LLM_MODEL", "gemini-2.5-flash")

SYSTEM = """You are a careful medical-document transcriber. You receive a photograph of a
laboratory report. Your ONLY job is to read what is printed on it.

Rules:
- Transcribe each test exactly: name, value, unit, and the reference range printed on the
  sheet if present. Copy the reference range verbatim as text (e.g. "13.5 - 17.5", "<200").
- Never invent, round, or infer a value you cannot actually read. If a value is unclear,
  use null and add the name to "unreadable".
- Do NOT interpret or comment on any result. Transcription only.
- If the image is not a lab report (e.g. a photo of a person, a receipt, a blank page),
  set "is_lab_report": false and return an empty results list.

Return ONLY a JSON object:
{
  "is_lab_report": boolean,
  "lab_name": string|null,
  "collection_date": string|null,
  "results": [
    {"test_name": string, "value": number|string|null, "unit": string|null,
     "reference_range": string|null, "flag_on_report": string|null}
  ],
  "unreadable": [string]
}"""


def _prepare(image: Image.Image, max_dim: int = 1600):
    rgb = image.convert("RGB")
    w, h = rgb.size
    if max(w, h) > max_dim:
        s = max_dim / float(max(w, h))
        rgb = rgb.resize((int(w * s), int(h * s)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    rgb.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    for attempt in (
        lambda t: json.loads(t),
        lambda t: json.loads(re.search(r"```(?:json)?\s*(\{.*?\})\s*```", t, re.DOTALL).group(1)),
        lambda t: json.loads(t[t.find("{"): t.rfind("}") + 1]),
    ):
        try:
            got = attempt(text)
            if isinstance(got, dict):
                return got
        except Exception:
            continue
    return {}


def extract(image: Image.Image) -> dict:
    """Transcribe a lab-report image. Always returns a dict; never raises."""
    b64 = _prepare(image)
    data_url = f"data:image/jpeg;base64,{b64}"
    payload = {
        "model": MODEL,
        "temperature": 0.0,
        # Gemini 2.5 Flash is a thinking model and its reasoning tokens count against
        # max_tokens. At 300 the whole budget was eaten by thinking and the answer came
        # back truncated at 9 tokens (finish_reason "length"). 4000 leaves room for the
        # reasoning AND the full transcription (measured: finish "stop", 21 rows).
        "max_tokens": 4000,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": [
                {"type": "text", "text": "Transcribe this lab report to JSON."},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]},
        ],
    }
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.load(r)
        msg = out["choices"][0]["message"]
        # some routers put the answer in reasoning; try content then reasoning
        raw = msg.get("content") or msg.get("reasoning") or ""
        parsed = _extract_json(raw)
    except Exception as exc:
        return {"ok": False, "error": f"vision call failed: {exc}", "results": []}

    if not parsed:
        return {"ok": False, "error": "model returned no parseable JSON", "results": []}
    parsed["ok"] = True
    return parsed
