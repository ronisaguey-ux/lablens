"""Analysis: turn transcribed values into flags and plain-language explanations.

This module is deliberately the ONLY place that interprets anything. It never
diagnoses. For each value it decides normal/high/low against the range printed on
the report (or the knowledge-base range as a fallback), attaches the grounded
explanation from the knowledge base, and raises an URGENT banner only for values
that cross a published critical threshold. It also merges multiple reports into a
per-analyte trend so a single value can be read in context.
"""
from . import reference

KB = reference.KnowledgeBase()


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def analyze_report(extraction: dict) -> dict:
    """Annotate each transcribed result. Returns the full analysis payload."""
    results = []
    urgent = []
    unreadable = []
    matched_count = 0

    for row in extraction.get("results", []) or []:
        name = (row.get("test_name") or "").strip()
        value = row.get("value")
        unit = row.get("unit") or ""
        printed = row.get("reference_range")
        kb = KB.match(name) if name else None

        v = _num(value)
        if v is None:
            unreadable.append(name or "(unnamed row)")
            results.append({
                "test_name": name, "value": value, "unit": unit,
                "flag": "unknown", "matched": bool(kb),
                "reason": "value could not be read from the report",
            })
            continue

        # Prefer the range printed on the report; fall back to the knowledge base.
        rng = reference.parse_range(printed)
        range_source = "report" if rng else None
        if not rng and kb:
            kref = kb.get("ref", {})
            rng = (kref.get("low"), kref.get("high"))
            range_source = "knowledge base"
        low, high = rng if rng else (None, None)

        flag = reference.flag_value(v, low, high)
        item = {
            "test_name": name, "value": v, "unit": unit,
            "reference_range": printed,
            "range_used": {"low": low, "high": high, "source": range_source},
            "flag": flag, "matched": bool(kb),
        }

        if kb:
            matched_count += 1
            item["analyte"] = kb["name"]
            item["category"] = kb.get("category")
            item["plain"] = kb.get("plain")
            item["why_matters"] = kb.get("why_matters")
            if flag == "high":
                item["meaning"] = kb.get("high_means")
            elif flag == "low":
                item["meaning"] = kb.get("low_means")
            else:
                item["meaning"] = "Within the expected range."
            # sex-specific note if the KB carries one
            if kb.get("ref", {}).get("sex_note"):
                item["note"] = kb["ref"]["sex_note"]

            # critical thresholds -> urgent, never silently normal
            ch, cl = kb.get("critical_high"), kb.get("critical_low")
            if ch is not None and v >= ch:
                urgent.append({"analyte": kb["name"], "value": v, "unit": unit,
                               "direction": "high", "threshold": ch})
            if cl is not None and v <= cl:
                urgent.append({"analyte": kb["name"], "value": v, "unit": unit,
                               "direction": "low", "threshold": cl})
        else:
            item["note"] = ("No plain-language entry for this test yet - the value is shown "
                            "but not interpreted.")
        results.append(item)

    abnormal = [r for r in results if r.get("flag") in ("high", "low")]
    return {
        "lab_name": extraction.get("lab_name"),
        "collection_date": extraction.get("collection_date"),
        "results": results,
        "summary": {
            "total": len(results),
            "abnormal": len(abnormal),
            "normal": len([r for r in results if r.get("flag") == "normal"]),
            "unmatched": len([r for r in results if not r.get("matched")]),
            "matched": matched_count,
        },
        "urgent": urgent,
        "unreadable": unreadable + list(extraction.get("unreadable", []) or []),
        "disclaimer": (
            "LabLens explains the numbers on a lab report in plain language. It is not a "
            "medical device and does not diagnose, treat, or replace a clinician. Reference "
            "ranges differ between labs - where the report prints its own range, that range "
            "was used. Take this to a healthcare professional to interpret in your context."
        ),
    }


def merge_trends(history: list) -> list:
    """history: list of analyze_report payloads (oldest first). Returns per-analyte series.

    Only analytes matched to the knowledge base are trended, so a trend line always has
    a consistent identity (a lab that prints 'Hgb' one month and 'Hemoglobin' the next
    still joins up).
    """
    series = {}
    for payload in history:
        date = payload.get("collection_date") or "unknown date"
        for r in payload.get("results", []):
            key = r.get("analyte") or r.get("test_name")
            if not key:
                continue
            v = _num(r.get("value"))
            if v is None:
                continue
            s = series.setdefault(key, {"analyte": key, "category": r.get("category"),
                                        "unit": r.get("unit"), "points": []})
            s["points"].append({"date": date, "value": v, "flag": r.get("flag")})
    return list(series.values())
