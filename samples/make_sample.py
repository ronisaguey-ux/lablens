#!/usr/bin/env python3
"""Generate a realistic synthetic lab report image for local testing/demo.

No real patient data - the values are hand-chosen so the panel includes a mix of
normal and abnormal results (high glucose/LDL/TSH, low hemoglobin/HDL) and one
value that crosses a critical threshold case would be easy to add.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

ROWS = [
    ("Test", "Result", "Units", "Reference Range"),
    ("WBC", "7.2", "10^3/uL", "4.0 - 11.0"),
    ("RBC", "4.85", "10^6/uL", "4.5 - 5.9"),
    ("Hemoglobin", "11.2", "g/dL", "13.5 - 17.5"),
    ("Hematocrit", "34.1", "%", "38.8 - 50.0"),
    ("MCV", "88", "fL", "80 - 100"),
    ("Platelets", "245", "10^3/uL", "150 - 400"),
    ("Glucose, Fasting", "118", "mg/dL", "70 - 99"),
    ("Hemoglobin A1c", "6.1", "%", "4.0 - 5.6"),
    ("Sodium", "139", "mmol/L", "135 - 145"),
    ("Potassium", "4.3", "mmol/L", "3.5 - 5.1"),
    ("Creatinine", "0.9", "mg/dL", "0.7 - 1.3"),
    ("ALT", "28", "U/L", "7 - 56"),
    ("AST", "24", "U/L", "10 - 40"),
    ("Total Cholesterol", "221", "mg/dL", "<200"),
    ("LDL Cholesterol", "142", "mg/dL", "<100"),
    ("HDL Cholesterol", "38", "mg/dL", ">40"),
    ("Triglycerides", "168", "mg/dL", "<150"),
    ("TSH", "6.8", "mIU/L", "0.4 - 4.0"),
    ("Vitamin D, 25-Hydroxy", "18", "ng/mL", "30 - 100"),
    ("Ferritin", "14", "ng/mL", "30 - 300"),
]


def _font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_report(path: str = "samples/sample_report.png"):
    W, H = 1000, 1180
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    f_head = _font(30)
    f_sub = _font(20)
    f_cell = _font(22)
    f_mono = _font(21)

    d.text((40, 34), "MERIDIAN DIAGNOSTIC LABORATORIES", font=f_head, fill="black")
    d.text((40, 78), "Patient: J. Doe        DOB: 01/02/1990        Sex: Female", font=f_sub, fill="black")
    d.text((40, 106), "Collected: 2026-09-18        Report: 2026-09-19", font=f_sub, fill="black")
    d.text((40, 134), "Panel: Comprehensive Metabolic + CBC + Lipid + Thyroid", font=f_sub, fill="black")
    d.line((40, 172, W - 40, 172), fill="black", width=2)

    y = 190
    col = [46, 470, 640, 800]
    for i, (c0, c1, c2, c3) in enumerate(ROWS):
        f = f_sub if i == 0 else f_mono
        fill = "black"
        d.text((col[0], y), c0, font=f, fill=fill)
        d.text((col[1], y), c1, font=f, fill=fill)
        d.text((col[2], y), c2, font=f, fill=fill)
        d.text((col[3], y), c3, font=f, fill=fill)
        y += 42
        if i == 0:
            d.line((40, y - 8, W - 40, y - 8), fill="black", width=1)

    d.text((40, y + 24), "Method: automated analyzer. Ranges are for adults; interpret with a clinician.",
           font=_font(18), fill="black")
    img.save(path)
    print("wrote", path, img.size)


if __name__ == "__main__":
    make_report(sys.argv[1] if len(sys.argv) > 1 else "samples/sample_report.png")
