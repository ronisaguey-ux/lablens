# LabLens — submission pack (ready to paste)

Everything below is pre-written so submitting is a couple of minutes of copy-paste.
Bob has a Devpost account from the ForgeHacks entry (Google login). Account actions and
the final submit are his; this pack removes every other step.

Repo (public): https://github.com/ronisaguey-ux/lablens
Demo video: `LabLens-demo.mp4` (also on the repo; upload to YouTube unlisted if a URL is required)

---

## Common fields (both events)

**Project name**
```
LabLens
```

**Tagline (≤ ~120 chars)**
```
Photograph a lab report — LabLens reads the numbers, flags what's out of range, and explains each in plain English.
```

**Built with**
```
python, flask, pillow, opencv-style vision pipeline via an OpenAI-compatible endpoint, gemini-2.5-flash, html, css, javascript
```

**Links**
- GitHub: https://github.com/ronisaguey-ux/lablens
- Video: **needs a public URL.** The demo file is in the repo (`LabLens-demo.mp4`, 1.7 MB).
  Uploading it to YouTube from here failed: the Chrome profile copy is not signed in to Google
  (`accounts.google.com/signin` redirect) — a credentials wall, not a code one. Bob uploads it
  unlisted in ~30s, or gives a moment to re-auth and I do it.
- App: runs locally — `pip install -r requirements.txt && ./run.sh` → http://127.0.0.1:5091

**"What did you learn" / challenges (short)**
```
The hard part was not reading the numbers — it was not overclaiming. A model that "interprets"
a blood test can invent a plausible-wrong medical claim. So the design splits the work: the
vision model only transcribes, a curated knowledge base does the explaining, and the reference
range printed on the user's own report wins over any generic range. That makes a confident wrong
answer structurally hard, which is the property that matters for a health tool.
```

---

## Description (markdown — works for both)

```markdown
## The problem

People get their lab results as a page of numbers and abbreviations and are told to "discuss it
with a doctor" — weeks later. They can't tell which of the twenty values matters, what "MCV 88 fL"
is, or whether a flag means anything. The dangerous failure isn't confusion; it's **false
reassurance** from a table that looks fine.

## What LabLens does

You photograph the report. LabLens:

1. **Reads** every value with a vision model — transcription only. Values it can't read are named,
   never guessed.
2. **Flags** each value against the reference range **printed on the report itself**, falling back
   to a curated knowledge base only when the sheet omits one — and it always says which range it used.
3. **Explains** every out-of-range value in plain English: what the test is, what a persistent high
   or low can mean, and why it matters.
4. **Warns honestly** — values crossing a published critical threshold get their own "discuss this
   promptly" banner, not a row buried in a table.
5. **Trends your history** across reports, joining an analyte even when two labs abbreviate it
   differently.

## Why it's different

The model transcribes; a knowledge base interprets; the report's own ranges win. Health tools fail
by being confidently wrong. This one is designed so it can't be: every claim traces to a reference
range, a curated entry, or is explicitly marked unreadable.

## Honest limits

It explains, it does not diagnose. It is not a medical device. Reference ranges differ by lab, sex
and age. The knowledge base covers 26 common analytes; anything unmatched is shown but not
interpreted, and that is stated. Trends need more than one report.

## Verified

On a photographed synthetic panel: 20 values read in ~13 s on CPU, 11 flagged out of range (matching
the abnormalities built into the sample), 9 in range, every explanation rendered, zero browser
console errors. The demo video is unedited footage of the running app.
```

---

## Event A — DSH Hacks V2 (13+, AI + healthcare, submit ~Nov 8)

- Track/theme: **AI + healthcare**
- ⚠ **Eligibility:** rules require "a member of an educational institution". Bob left school.
  Decide: (a) state the school of record he is still entitled to, or (b) message the organisers
  first. **Do not hide it** — the rules treat a false eligibility claim as disqualifying.
- Prize note: the "$100k+" title is marketing; the real cash is 1st $3,928 / 2nd $3,543 / 3rd $3,363.

## Event B — UnivaBio (13+ students, AI for Human Health, **closes Oct 13 11:45pm EDT**)

- Eligibility: "All students aged 13+". Same school-status question, lower stakes.
- Prize note: "$40,000" is mostly credits/memberships; some cash tiers.
- Required assets: interactive project + demo video + **one-page PDF** + GitHub repo.
  - PDF: `LabLens-one-page.pdf` (built)
  - Video: `LabLens-demo.mp4` (built)
  - Repo: pushed (built)

---

## The one decision Bob must make

DSH (and to a lesser degree UnivaBio) assume the entrant is a **student at an educational
institution**. Bob is 16 and left school. Options: state a school of record, or ask the organisers
before submitting. This is deliberately left for Bob — it is an eligibility statement in his name.
