"""Analyte knowledge base: matching a report's test name to a known analyte, and
parsing the reference range printed on the report.

The report's OWN range wins when present: labs calibrate differently, and a value
can be flagged normal on one lab's sheet and abnormal against another's. The KB
range is only the fallback, and every response says which range was used.
"""
import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(_HERE, "..", "data", "analytes.json")


def _norm(s: str) -> str:
    """Lowercase, drop punctuation/parentheticals so 'ALT (SGPT)' -> 'alt sgpt'."""
    s = (s or "").lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


class KnowledgeBase:
    def __init__(self, path: str = KB_PATH):
        with open(path) as f:
            data = json.load(f)
        self.analytes = data["analytes"]
        self.meta = data.get("_meta", {})
        # build a lookup from every synonym and the canonical name
        self._index = {}
        for a in self.analytes:
            keys = [a["name"]] + list(a.get("synonyms", [])) + [a["id"]]
            for k in keys:
                self._index[_norm(k)] = a

    # ---- matching -----------------------------------------------------------
    def match(self, test_name: str):
        """Return the KB analyte for a report test name, or None.

        Strategy, most specific first:
          1. exact normalised synonym match
          2. the report name contains a synonym as a whole phrase
          3. token overlap (Jaccard >= 0.5) as a last resort
        Deliberately conservative: a wrong match would attach the wrong explanation
        to a number, which is worse than showing the raw value with no commentary.
        """
        n = _norm(test_name)
        if not n:
            return None
        if n in self._index:
            return self._index[n]

        # whole-phrase containment
        for key, a in self._index.items():
            if len(key) >= 4 and re.search(rf"\b{re.escape(key)}\b", n):
                return a

        # token overlap
        nt = set(n.split())
        best, best_score = None, 0.0
        for key, a in self._index.items():
            kt = set(key.split())
            if not kt:
                continue
            score = len(nt & kt) / len(nt | kt)
            if score > best_score:
                best, best_score = a, score
        return best if best_score >= 0.5 else None


def parse_range(text: str):
    """Parse a printed reference range into (low, high) floats, each possibly None.

    Handles '13.5 - 17.5', '70-99', '<200', '≤ 5.6', 'greater than 40', '> 40',
    '135 – 145' (en dash), and ranges with units glued on ('4.0-11.0 10^3/uL').
    Returns None if nothing numeric could be read (caller falls back to the KB).

    The dash form is matched FIRST and explicitly: a naive float scan reads '70-99'
    as the two numbers 70 and -99, which produced a nonsense range of (-99, 70).
    """
    if not text:
        return None
    t = (text or "").strip()
    t = t.replace("–", "-").replace("—", "-").replace("≤", "<").replace("≥", ">")

    # 1. explicit "A - B" (the common case) - also stops the unit's digits being read
    m = re.search(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", t)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        return (min(a, b), max(a, b))

    # 2. one-sided bounds
    if t.lstrip().startswith("<") or re.search(r"less than", t, re.I):
        nums = re.findall(r"\d+(?:\.\d+)?", t)
        return (None, float(nums[0])) if nums else None
    if t.lstrip().startswith(">") or re.search(r"greater than|above", t, re.I):
        nums = re.findall(r"\d+(?:\.\d+)?", t)
        return (float(nums[0]), None) if nums else None

    return None


def flag_value(value, low, high):
    """Return 'high' | 'low' | 'normal' | 'unknown' given a value and bounds."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if low is not None and v < low:
        return "low"
    if high is not None and v > high:
        return "high"
    return "normal"
