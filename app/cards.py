import cv2
import numpy as np

SUPPORTED_DICTIONARIES = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
}

ANSWER_ROTATIONS = {"A": 0, "B": 3, "C": 2, "D": 1}

WHITE = 255
BLACK = 0
FONT = cv2.FONT_HERSHEY_SIMPLEX
MARKER_FRACTION = 0.52


class UnknownDictionaryError(ValueError):
    pass


def marker_capacity(dictionary_name):
    return int(_dictionary(dictionary_name).bytesList.shape[0])


def render_card(marker_id, dictionary_name, label, size):
    dictionary = _dictionary(dictionary_name)
    capacity = int(dictionary.bytesList.shape[0])

    if not 0 <= marker_id < capacity:
        raise ValueError(f"{dictionary_name} holds marker ids 0 to {capacity - 1}")

    canvas = np.full((size, size), WHITE, dtype=np.uint8)

    marker_size = int(size * MARKER_FRACTION)
    marker = cv2.aruco.generateImageMarker(dictionary, marker_id, marker_size)

    offset = (size - marker_size) // 2
    canvas[offset:offset + marker_size, offset:offset + marker_size] = marker

    _draw_answer_letters(canvas, size, offset)
    _draw_header(canvas, size, marker_id, label)

    success, buffer = cv2.imencode(".png", canvas)

    if not success:
        raise RuntimeError("Could not encode the card as PNG")

    return buffer.tobytes()


def _dictionary(dictionary_name):
    if dictionary_name not in SUPPORTED_DICTIONARIES:
        raise UnknownDictionaryError(
            f"Unsupported dictionary {dictionary_name}. "
            f"Use one of {', '.join(sorted(SUPPORTED_DICTIONARIES))}"
        )

    return cv2.aruco.getPredefinedDictionary(SUPPORTED_DICTIONARIES[dictionary_name])


def _draw_answer_letters(canvas, size, offset):
    tile_size = int(offset * 0.8)
    scale = tile_size / 40.0
    thickness = max(2, int(scale * 2))

    for letter, rotations in ANSWER_ROTATIONS.items():
        tile = np.full((tile_size, tile_size), WHITE, dtype=np.uint8)
        (text_width, text_height), _ = cv2.getTextSize(letter, FONT, scale, thickness)
        origin = ((tile_size - text_width) // 2, (tile_size + text_height) // 2)
        cv2.putText(tile, letter, origin, FONT, scale, BLACK, thickness, cv2.LINE_AA)

        top, left = _letter_position(letter, size, offset, tile_size)
        canvas[top:top + tile_size, left:left + tile_size] = np.rot90(tile, rotations)


def _letter_position(letter, size, offset, tile_size):
    centred = (size - tile_size) // 2
    near_edge = (offset - tile_size) // 2
    far_edge = size - offset + near_edge

    positions = {
        "A": (near_edge, centred),
        "B": (centred, far_edge),
        "C": (far_edge, centred),
        "D": (centred, near_edge),
    }

    return positions[letter]


def _draw_header(canvas, size, marker_id, label):
    scale = size / 900.0
    text = f"{label}  -  Card {marker_id}" if label else f"Card {marker_id}"
    thickness = max(1, int(2 * scale))
    font_scale = 0.8 * scale

    (text_width, _), _ = cv2.getTextSize(text, FONT, font_scale, thickness)
    origin = ((size - text_width) // 2, int(size * 0.04))

    cv2.putText(canvas, text, origin, FONT, font_scale, BLACK, thickness, cv2.LINE_AA)
