"""
Hand Gesture Recognition System
Optimized for file-based backend processing.

Public API
----------
detect_gestures(image_path, model_path) -> list[dict] | None
"""

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2


# ═══════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════

# ─── LANDMARK INDICES (MediaPipe Hand) ───────────────────────────────────
#   4=THUMB_TIP   8=INDEX_TIP   12=MIDDLE_TIP   16=RING_TIP   20=PINKY_TIP
#   3=THUMB_IP    7=INDEX_DIP   11=MIDDLE_DIP   15=RING_DIP   19=PINKY_DIP
#   2=THUMB_MCP   6=INDEX_PIP   10=MIDDLE_PIP   14=RING_PIP   18=PINKY_PIP
#   1=THUMB_CMC   5=INDEX_MCP    9=MIDDLE_MCP   13=RING_MCP   17=PINKY_MCP
#                  0=WRIST
# ─────────────────────────────────────────────────────────────────────────

_FINGER_TIPS = [8, 12, 16, 20]
_FINGER_PIPS = [6, 10, 14, 18]
_THUMB_TIP   = 4
_THUMB_IP    = 3


# ═══════════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════════

def _is_palm_facing_camera(lm, handedness_label: str) -> bool:
    """
    Compare Index MCP (5) vs Pinky MCP (17) x-position to determine
    whether the palm faces the camera or faces away.
    """
    if handedness_label == "Right":
        return lm[5].x < lm[17].x
    return lm[5].x > lm[17].x


def _fingers_up(lm, handedness_label: str) -> list[bool]:
    """Return [thumb, index, middle, ring, pinky] extension booleans."""
    palm_facing = _is_palm_facing_camera(lm, handedness_label)

    if handedness_label == "Right":
        thumb_up = lm[_THUMB_TIP].x < lm[_THUMB_IP].x if palm_facing \
              else lm[_THUMB_TIP].x > lm[_THUMB_IP].x
    else:
        thumb_up = lm[_THUMB_TIP].x > lm[_THUMB_IP].x if palm_facing \
              else lm[_THUMB_TIP].x < lm[_THUMB_IP].x

    return [thumb_up] + [
        lm[tip].y < lm[pip].y
        for tip, pip in zip(_FINGER_TIPS, _FINGER_PIPS)
    ]


def _classify_gesture(lm, handedness_label: str) -> str:
    """Map finger extension pattern to a gesture label."""
    f = _fingers_up(lm, handedness_label)

    _GESTURE_MAP = {
        (False, False, False, False, False): "Fist",
        (True,  True,  True,  True,  True ): "Open Hand",
        (False, True,  False, False, False): "Pointing",
        (False, True,  True,  False, False): "Peace",
        (True,  False, False, False, True ): "Call Me",
        (True,  True,  True,  True,  False): "Four Fingers",
        (False, False, False, False, True ): "Pinky Up",
        (True,  False, False, False, False): "Thumbs Up",
        (False, True,  True,  True,  True ): "Four (No Thumb)",
    }

    return _GESTURE_MAP.get(tuple(f), "Unknown")


# ═══════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════

def detect_gestures(
    image_path: str,
    model_path: str = "hand_landmarker.task",
    num_hands: int = 2,
) -> list[dict] | None:
    """
    Detect and classify hand gestures in an image file.

    Parameters
    ----------
    image_path : Path to the input image (.jpg, .jpeg, .png, .bmp, .webp).
    model_path : Path to the MediaPipe hand_landmarker.task model file.
    num_hands  : Maximum number of hands to detect (default: 2).

    Returns
    -------
    List of dicts (one per detected hand), each containing:
        "hand"       – "Left" or "Right"
        "gesture"    – classified gesture label (str)
        "confidence" – handedness detection confidence (0.0–1.0)
        "landmarks"  – list of 21 dicts with normalised {x, y, z} coords
    Returns None if the image cannot be loaded.
    Returns an empty list [] if no hands are detected.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Cannot read image: '{image_path}'")

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
    )

    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=model_path),
        num_hands=num_hands,
    )

    with vision.HandLandmarker.create_from_options(options) as detector:
        result = detector.detect(mp_image)

    if not result.hand_landmarks:
        return []

    hands = []
    for landmarks, handedness in zip(result.hand_landmarks, result.handedness):
        label      = handedness[0].category_name
        confidence = round(handedness[0].score, 4)
        gesture    = _classify_gesture(landmarks, label)

        hands.append({
            "hand":       label,
            "gesture":    gesture,
            "confidence": confidence,
        })

    return hands