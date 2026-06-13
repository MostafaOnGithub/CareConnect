"""
One-Shot Face Recognition System
Optimized for file-based backend processing.

Public API
----------
register_face(person_name, image_path, db_path, overwrite) -> bool
recognize_face(image_path, db_path, threshold)             -> dict | None
"""

import cv2
import numpy as np
import json
import os
from scipy.spatial.distance import euclidean
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════════

def _load_detector():
    """Return (detector, use_mediapipe). Prefers MediaPipe, falls back to Haar."""
    try:
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        base_options = python.BaseOptions(model_asset_path="face_landmarker.task")
        options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)
        detector = vision.FaceLandmarker.create_from_options(options)
        return detector, True
    except Exception:
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        return cascade, False


def _detect_faces(image_bgr, detector, use_mediapipe: bool) -> list[tuple]:
    """Return list of (x1, y1, x2, y2) bounding boxes."""
    if use_mediapipe:
        try:
            import mediapipe as mp
            h, w = image_bgr.shape[:2]
            rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = detector.detect(mp_image)
            boxes = []
            if result.face_landmarks:
                for landmarks in result.face_landmarks:
                    xs = [lm.x for lm in landmarks]
                    ys = [lm.y for lm in landmarks]
                    x1 = max(0, int(min(xs) * w) - 10)
                    y1 = max(0, int(min(ys) * h) - 10)
                    x2 = min(w, int(max(xs) * w) + 10)
                    y2 = min(h, int(max(ys) * h) + 10)
                    boxes.append((x1, y1, x2, y2))
            return boxes
        except Exception:
            pass  # fall through to cascade

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
    return [(x, y, x + w, y + h) for (x, y, w, h) in faces] if len(faces) else []


def _extract_face_region(image_path: str, detector, use_mediapipe: bool) -> np.ndarray | None:
    """Load image from path and return the first detected face as 64×64 crop."""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Cannot read image: '{image_path}'")

    boxes = _detect_faces(image, detector, use_mediapipe)
    if not boxes:
        return None

    x1, y1, x2, y2 = boxes[0]
    roi = image[y1:y2, x1:x2]
    return cv2.resize(roi, (64, 64))


def _compute_lbp(gray: np.ndarray) -> np.ndarray:
    """Uniform Local Binary Pattern encoding."""
    lbp = np.zeros_like(gray, dtype=np.uint8)
    neighbours = [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0,  1), ( 1, 1), ( 1, 0),
        ( 1, -1), ( 0, -1),
    ]
    for bit, (dy, dx) in enumerate(neighbours):
        shifted = np.roll(np.roll(gray, dy, axis=0), dx, axis=1)
        lbp |= (gray >= shifted).astype(np.uint8) << bit
    return lbp


def _compute_embedding(face_image: np.ndarray) -> np.ndarray | None:
    """
    Build a 288-d discriminative embedding from a 64×64 face crop.
    Features: LBP histogram (32) + cell mean/std (128) + HOG-lite (128).
    """
    if face_image is None:
        return None

    gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (64, 64)).astype(np.float32)
    features = []

    # 1. LBP histogram (32 bins)
    lbp = _compute_lbp(gray.astype(np.uint8))
    hist_lbp, _ = np.histogram(lbp, bins=32, range=(0, 256))
    hist_lbp = hist_lbp.astype(np.float32)
    norm = np.linalg.norm(hist_lbp)
    if norm > 0:
        hist_lbp /= norm
    features.extend(hist_lbp)

    # 2. Cell-wise mean/std over 8×8 grid (128 values)
    cell_stats = []
    for i in range(0, 64, 8):
        for j in range(0, 64, 8):
            cell = gray[i:i + 8, j:j + 8]
            cell_stats.extend([np.mean(cell), np.std(cell)])
    cell_stats = np.array(cell_stats, dtype=np.float32)
    norm = np.linalg.norm(cell_stats)
    if norm > 0:
        cell_stats /= norm
    features.extend(cell_stats)

    # 3. HOG-lite: gradient orientation histograms (128 values)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)
    orientation = np.arctan2(sobely, sobelx)

    for i in range(0, 64, 16):
        for j in range(0, 64, 16):
            b_mag = magnitude[i:i + 16, j:j + 16]
            b_ori = orientation[i:i + 16, j:j + 16]
            hist, _ = np.histogram(b_ori, bins=8, range=(-np.pi, np.pi), weights=b_mag)
            hist = hist.astype(np.float32)
            bn = np.linalg.norm(hist)
            if bn > 0:
                hist /= bn
            features.extend(hist)

    # Global L2 normalisation
    embedding = np.array(features, dtype=np.float32)
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding /= norm
    return embedding


def _cosine_similarity(e1: np.ndarray, e2: np.ndarray) -> float:
    """Raw cosine similarity in [0, 1] for non-negative unit vectors."""
    n1, n2 = np.linalg.norm(e1), np.linalg.norm(e2)
    if n1 > 0 and n2 > 0:
        return float(np.clip(np.dot(e1, e2) / (n1 * n2), 0.0, 1.0))
    return 0.0


def _load_db(db_path: str) -> dict:
    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            return json.load(f)
    return {}


def _save_db(db: dict, db_path: str) -> None:
    with open(db_path, "w") as f:
        json.dump(db, f, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════

def register_face(
    person_name: str,
    image_path: str,
    db_path: str = "face_embeddings_db.json",
    overwrite: bool = False,
) -> bool:
    """
    Register a person's face embedding from an image file.

    Parameters
    ----------
    person_name : Unique identifier for the person.
    image_path  : Path to the source image file.
    db_path     : Path to the JSON embedding database (created if absent).
    overwrite   : Replace an existing registration when True.

    Returns
    -------
    True on success, False otherwise.
    """
    db = _load_db(db_path)

    if person_name in db and not overwrite:
        raise ValueError(f"'{person_name}' is already registered. Pass overwrite=True to replace.")

    detector, use_mediapipe = _load_detector()
    face_region = _extract_face_region(image_path, detector, use_mediapipe)
    if face_region is None:
        raise RuntimeError(f"No face detected in '{image_path}'.")

    embedding = _compute_embedding(face_region)
    if embedding is None:
        raise RuntimeError("Embedding computation failed.")

    db[person_name] = {
        "embedding": embedding.tolist(),
        "image_path": image_path,
        "timestamp": datetime.now().isoformat(),
    }
    _save_db(db, db_path)
    return True


def recognize_face(
    image_path: str,
    db_path: str = "face_embeddings_db.json",
    threshold: float = 0.75,
) -> dict | None:
    """
    Identify the closest registered face in an image file.

    Parameters
    ----------
    image_path : Path to the query image file.
    db_path    : Path to the JSON embedding database.
    threshold  : Minimum cosine similarity to accept a match.

    Returns
    -------
    dict with keys:
        "name"       – matched person name, or "Unknown"
        "confidence" – cosine similarity score (0–1)
        "matched"    – True if confidence >= threshold
    Returns None if no face is detected in the image.
    """
    db = _load_db(db_path)
    if not db:
        raise RuntimeError("Database is empty — register faces first.")

    detector, use_mediapipe = _load_detector()
    face_region = _extract_face_region(image_path, detector, use_mediapipe)
    if face_region is None:
        return None

    embedding = _compute_embedding(face_region)
    if embedding is None:
        return None

    emb_array = np.array(embedding, dtype=np.float32)
    scores = {
        name: _cosine_similarity(emb_array, np.array(data["embedding"], dtype=np.float32))
        for name, data in db.items()
    }
    best_name = max(scores, key=scores.get)
    best_conf = scores[best_name]

    return {
        "name": best_name if best_conf >= threshold else "Unknown",
        "confidence": round(best_conf, 4),
        "matched": best_conf >= threshold,
    }