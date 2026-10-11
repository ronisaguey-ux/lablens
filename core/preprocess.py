"""Preprocessing for a photographed report — the difference between a clean scan and a
phone photo taken at an angle in bad light.

Real users photograph paper: slightly rotated, unevenly lit, a bit soft. The vision model
tolerates some of that and fails quietly on the rest, so the image is cleaned BEFORE it is
sent. Steps, in order:

  1. upscale if the long edge is small (more pixels for the model to read),
  2. estimate and undo rotation (deskew) using the dominant text-line angle,
  3. normalise contrast locally (CLAHE) and sharpen a touch,
  4. flatten the page to grayscale-on-white so shadows do not become "signal".

Every step is optional and guarded: if OpenCV is not installed, or a step cannot find the
structure it needs, the image passes through unchanged. Preprocessing must never make an
image worse or crash the request.
"""
import io

try:
    import cv2
    import numpy as np
    _CV2 = True
except Exception:  # pragma: no cover - exercised only when cv2 is absent
    _CV2 = False

from PIL import Image

MIN_LONG_EDGE = 1400          # below this, upscale: small text needs pixels
MAX_LONG_EDGE = 2200          # above this, downscale: the model gets no benefit
MAX_SKEW_DEG = 15.0           # only correct plausible page skew, never a 40-degree photo


def _pil_to_cv(img: Image.Image):
    arr = np.array(img.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def _cv_to_pil(arr):
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))


def _resize_if_needed(gray):
    h, w = gray.shape[:2]
    long_edge = max(h, w)
    if long_edge < MIN_LONG_EDGE:
        s = MIN_LONG_EDGE / long_edge
        gray = cv2.resize(gray, (int(w * s), int(h * s)), interpolation=cv2.INTER_CUBIC)
    elif long_edge > MAX_LONG_EDGE:
        s = MAX_LONG_EDGE / long_edge
        gray = cv2.resize(gray, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    return gray


def _estimate_skew(gray):
    """Dominant text-line angle in degrees, or 0.0 when no clear structure is found.

    Method: edges -> Hough line segments -> take each segment's angle, keep the ones close
    to horizontal (a report is mostly horizontal text), and return the median. The median
    rather than the mode so a single stray vertical rule cannot swing the correction.
    """
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=120,
                            minLineLength=max(60, gray.shape[1] // 8), maxLineGap=12)
    if lines is None:
        return 0.0
    # HoughLinesP returns (N,1,4) on some builds and (N,4) on others; reshape is safe for both
    # and avoids "cannot unpack non-iterable numpy.int32" when the leading dim is already gone.
    angles = []
    for x1, y1, x2, y2 in lines.reshape(-1, 4):
        ang = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        # fold into [-90, 90]; text lines are near 0 (or near 180, which folds to 0)
        if ang > 90:
            ang -= 180
        elif ang < -90:
            ang += 180
        if abs(ang) <= MAX_SKEW_DEG:
            angles.append(ang)
    if not angles:
        return 0.0
    return float(np.median(angles))


def _rotate(gray, angle):
    if abs(angle) < 0.2:
        return gray
    h, w = gray.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(gray, m, (w, h), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)


def _enhance(gray):
    # CLAHE: local contrast, so a shadow across one half of the page does not swallow the
    # text on that half while the other half is fine.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    out = clahe.apply(gray)
    # light unsharp mask to recover edge crispness lost to camera blur
    blur = cv2.GaussianBlur(out, (0, 0), 1.2)
    return cv2.addWeighted(out, 1.35, blur, -0.35, 0)


def preprocess(image: Image.Image, mode: str = "auto"):
    """Clean a report photo for extraction. Returns (PIL image, info dict).

    mode:
      "off"   - return the image unchanged (A/B comparisons, troubleshooting)
      "auto"  - upscale if small, deskew, enhance (the default)
      "auto-no-deskew" - everything except rotation (to isolate deskew's effect)
    info records what each step did, so the UI (and a reviewer) can see it.
    """
    info = {"cv2": _CV2, "mode": mode, "steps": []}
    if mode == "off" or not _CV2:
        if not _CV2:
            info["note"] = "OpenCV not available - image passed through unchanged"
        return image, info

    try:
        bgr = _pil_to_cv(image)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        before = gray.shape[:2]

        gray = _resize_if_needed(gray)
        if gray.shape[:2] != before:
            info["steps"].append(f"resized {before[::-1]}->{gray.shape[1::-1]}")

        if mode == "auto":
            ang = _estimate_skew(gray)
            if abs(ang) >= 0.2:
                gray = _rotate(gray, ang)
                info["steps"].append(f"deskewed {ang:+.2f} deg")
            else:
                info["steps"].append("skew < 0.2 deg (no rotation)")

        gray = _enhance(gray)
        info["steps"].append("CLAHE contrast + unsharp")
        return Image.fromarray(gray).convert("RGB"), info
    except Exception as exc:  # never let preprocessing break a request
        info["note"] = f"preprocessing skipped: {exc}"
        return image, info


def make_degraded(path_in: str, path_out: str, angle: float = 6.5, dim: float = 0.55):
    """Build a hard test image from a clean one: rotate and darken it.

    Used to prove preprocessing earns its place — a clean scan proves nothing.
    """
    if not _CV2:
        raise RuntimeError("cv2 required to make a degraded sample")
    img = Image.open(path_in)
    arr = _pil_to_cv(img)
    h, w = arr.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    rot = cv2.warpAffine(arr, m, (w, h), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    # uneven lighting: a linear gradient, so one side is much darker than the other
    grad = np.tile(np.linspace(dim, 1.0, w, dtype=np.float32), (h, 1))
    grad = cv2.merge([grad, grad, grad])
    out = np.clip(rot.astype(np.float32) * grad, 0, 255).astype(np.uint8)
    _cv_to_pil(out).save(path_out)
    return path_out
