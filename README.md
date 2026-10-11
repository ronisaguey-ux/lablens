# LabLens — understand your bloodwork

**Photograph a lab report. LabLens reads the numbers, flags what is out of range, and
explains each one in plain English — grounded in reference ranges, never a diagnosis.**

Entry for the **UnivaBio** and **DSH Hacks V2** hackathons (theme: *AI for Human Health*).

---

## The problem

Most people receive a lab report as a PDF of numbers and abbreviations and are expected to
"discuss it with their doctor" weeks later. They cannot tell which of the twenty values
matters, what "MCV 88 fL" even is, or whether a flag means anything. Health literacy is one
of the strongest predictors of health outcomes, and a lab report is exactly where it is
tested — at the moment of maximum confusion and minimum guidance.

The dangerous failure is not ignorance; it is **false reassurance**. A value can sit inside
a "normal" range and still be a concerning trend, and a slightly-high value can matter far
more than a slightly-lower one depending on what it is. Generic symptom checkers do not read
the actual numbers a person is holding.

## What LabLens does

1. **Reads the report.** A photo (or scan) is transcribed by a vision model into
   `{test, value, unit, reference-range}` — transcription only, no interpretation. Values it
   cannot read are marked unreadable rather than guessed.
2. **Flags against the right range.** Each value is judged against the reference range
   **printed on the report itself** wherever present, falling back to a curated knowledge
   base only when the sheet omits one. The app always states which range it used, because
   ranges differ between labs.
3. **Explains, grounded.** Every out-of-range value gets a plain-language entry drawn from a
   hand-built analyte knowledge base: what the test is, what a persistent high or low value
   can mean, and why it matters. Nothing is invented by the model at this stage.
4. **Warns honestly.** Values crossing a published critical threshold raise a distinct
   "discuss this promptly" banner — never buried in a normal-looking table.
5. **Trends your history.** Uploading more than one report shows each analyte's trajectory,
   joining reports even when the lab abbreviates the name differently.

## Why it can win

- **A specific, real problem** — the moment of reading a lab report, not health in general.
- **Grounded, not hallucinated** — the model transcribes; a knowledge base interprets; the
  report's own ranges win. The design makes a plausible-but-wrong medical claim structurally
  hard.
- **Honest limits** — it says what it cannot read, always shows which range it used, and
  tells the user at every step that it explains rather than diagnoses.
- **A working demo, not a mockup** — the whole pipeline runs on CPU against a photographed
  report.

## Verified results

Run locally on a photographed synthetic panel (`samples/sample_report.png`), Gemini Flash
vision via a local OpenAI-compatible router:

| What | Result |
|---|---|
| Values transcribed | **20 / 21 rows**, in ~13 s, on CPU |
| Matched to the knowledge base | 19 |
| Flagged out of range | **11** (6 high, 5 low) |
| In range | 9 |
| Range source used | the report's own printed ranges (source: `report`) |
| Explanations rendered | one per matched test, all grounded |
| Console errors in the browser | 0 |

Every flag in the run matched the abnormality deliberately built into the sample (low
hemoglobin/hematocrit/HDL/vitamin D/ferritin; high fasting glucose/A1c/cholesterol/LDL/
triglycerides/TSH).

## Run it

```sh
pip install -r requirements.txt
./run.sh                     # http://127.0.0.1:5091
```

LabLens talks to any OpenAI-compatible endpoint that serves a vision model:

```sh
export LLM_BASE_URL=http://127.0.0.1:8790/v1/chat/completions   # a local router...
export LLM_MODEL=gemini-2.5-flash                               # ...serving a vision model
```

Upload `samples/sample_report.png` to see a full run end to end.

## Architecture

```
 photo/scan ──▶ core/extract.py  (vision: transcribe only)
                     │  {test, value, unit, range printed on the sheet}
                     ▼
                core/analyze.py  (the ONLY place that interprets)
                     │  flag vs the report's own range, else the knowledge base
                     │  attach grounded explanation + critical-value banner
                     ▼
 data/analytes.json  (26 curated analytes: plain meaning, high/low, why it matters)
                     ▼
                 Flask UI  (app.py + templates/index.html)
```

## Honest limits

- It **explains**, it does not **diagnose**. It is not a medical device.
- Reference ranges differ by lab, sex, and age — the report's own range is used when
  printed; otherwise a general adult range, and the UI says so.
- The knowledge base covers 26 common analytes; unmatched tests are shown but not
  interpreted, and named.
- Trends need more than one report to be meaningful.
- It reads what is printed; a value it cannot read is reported as unreadable, never guessed.

## Licence

MIT.
