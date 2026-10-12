# NFTE World Series of Innovation — Impact League submission (draft)

**Challenge:** MetLife Foundation Good Health & Well-Being Challenge (SDG 3)
**Prompt:** Create opportunities that make healthy living easier, accessible, and more joyful for all
members of your community.
**Entrant:** Roni Saguey (age 16) · **Deadline:** December 13, 2026, 11:59 PM EST
**Submit at:** https://wsi.awardsplatform.com/ (account required)
**Scored on:** creativity · connection to the SDG · potential impact

---

## The idea (one line)

**LabLens** turns a blood-test result from a page of unexplained numbers into plain English — in
seconds, on a phone, with the explanation grounded in the reference ranges printed on the report
itself.

## The problem

A routine blood panel comes back as a grid of numbers with a "discuss with your clinician" note.
For millions of people that discussion is weeks away, or costs a copay, or happens in a language they
read slowly. In the gap, people either ignore results that matter or self-diagnose from search
results that are not about *their* numbers. Health literacy is the bottleneck — not the test.

## What it does

1. You photograph (or upload) the lab report.
2. LabLens reads each test row: name, value, units, and the reference range **from that report**.
3. It flags every value that sits outside range.
4. For each one it writes a plain-English explanation — what the test measures, what a high or low
   value can indicate, and why it matters — and, separately, warns when a value crosses a
   **critical** threshold.
5. It tracks results across reports so a user sees a trend instead of a snapshot.

**It explains. It does not diagnose.** Every screen says so, and the tool refuses to interpret a value
whose range the report does not print.

## Why it fits "good health and well-being"

- **Access:** works on a phone camera, no clinician appointment needed to *understand* your own data.
- **Equity:** plain language, not medical jargon; grounded in the report's own ranges, so it works for
  labs worldwide instead of assuming one country's units.
- **Joy/agency:** the win is comprehension — a person walks into their appointment already knowing
  what changed and what to ask.
- **Safety:** it is explicitly an explainer, not a diagnostic device, and says so on every result.

## Status (honest)

Built and working: the app reads a real photographed panel of 20 values in ~13s on CPU, flags the
out-of-range ones, explains each, and tracks trends across reports. It also cleans up a real phone
photo (deskew + contrast) before reading it. It is not a medical device and does not diagnose.

- Code: https://github.com/ronisaguey-ux/lablens
- Demo: recorded walkthrough of the real app.

## What the prize would fund

A pilot with a community clinic or school nurse so the explainer text is reviewed by a clinician
before wide use, plus translations beyond English.

---

### Submission checklist
- [x] Feasible, low-cost, real working prototype
- [x] Tied to SDG 3 with a named community benefit
- [x] Honest about limits (explainer, not diagnosis)
- [ ] Entrant account at wsi.awardsplatform.com + guardian agreement (Bob is 16)
- [ ] Pitch video (only needed if named a finalist — due March 2, 2027)
