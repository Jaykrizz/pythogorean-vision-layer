import math

import cv2
import numpy as np

from .cards import _dictionary

# Top edge of the marker, measured in the camera image.
# 0 degrees points right: the card is held with A at the top.
ANSWER_BY_QUADRANT = {0: "A", 90: "D", 180: "C", 270: "B"}


def detect_answers(image_bytes, dictionary_name):
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not read that image")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector = cv2.aruco.ArucoDetector(_dictionary(dictionary_name), cv2.aruco.DetectorParameters())
    corners, ids, _rejected = detector.detectMarkers(gray)

    if ids is None:
        return []

    best = {}
    for index, marker_id in enumerate(ids.flatten()):
        points = np.asarray(corners[index]).reshape(4, 2)
        letter = _answer_letter(points)
        size = _span(points)
        marker_key = int(marker_id)
        previous = best.get(marker_key)
        if previous is None or size > previous[0]:
            best[marker_key] = (size, letter)

    return [{"markerId": marker_id, "letter": letter} for marker_id, (_size, letter) in sorted(best.items())]


def _answer_letter(points):
    top_left, top_right = points[0], points[1]
    angle = math.degrees(math.atan2(top_right[1] - top_left[1], top_right[0] - top_left[0]))
    if angle < 0:
        angle += 360
    quadrant = int((angle + 45) // 90) % 4 * 90
    return ANSWER_BY_QUADRANT[quadrant]


def _span(points):
    width = float(np.linalg.norm(points[1] - points[0]))
    height = float(np.linalg.norm(points[3] - points[0]))
    return width * height
