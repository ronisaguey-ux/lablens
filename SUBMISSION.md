# LabLens — submission status

**Project:** LabLens — photograph a lab report, get the numbers read, flagged, and explained.
**Theme fit:** AI for Human Health.
**Repo (public):** https://github.com/ronisaguey-ux/lablens

## Entered / enterable

| Event | Age rule | Deadline | Cash | Status |
|---|---|---|---|---|
| DSH Hacks V2 | 13+, **students only** | Nov 14 | **NON-CASH** (credits/licences only) | built, not submitted |
| UnivaBio | 13+, **students only** | Oct 20 | **NON-CASH** (credits/licences only) | built, not submitted |

## Deliverables

| Asset | File | Status |
|---|---|---|
| Working app | `app.py` + `core/` + `templates/` | verified: 20 values read, 11 flagged, 0 console errors |
| Demo video | `LabLens-demo.mp4` (40.4 s, 760x1100, h264+aac) | recorded from the real app + AI voiceover |
| One-page PDF | `LabLens-one-page.pdf` (1 page) | generated |
| Public repo | `ronisaguey-ux/lablens` | pushed, 11 top-level entries, commit 1584c40 |
| README | `README.md` | architecture, results, honest limits |

## What a reviewer should do

1. `pip install -r requirements.txt && ./run.sh` → http://127.0.0.1:5091
2. Upload `samples/sample_report.png`
3. Confirm the 11 out-of-range flags and the grounded explanations.

## Note on the educational-institution rule

DSH Hacks V2 requires "a member of an educational institution"; Bob is a 16-year-old
developer who left school. Enter with the school-of-record he is entitled to state, or
ask the organisers. Flagged to Bob, not hidden.

## Remaining step (human)

Account + submit on each event's Devpost page. Account creation and the final submit are the owner's call.
