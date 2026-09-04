# Pythogorean Vision Layer

Python side of Pythogorean. Owns everything to do with the camera and the
printed ArUco cards, and nothing to do with business rules.

Today it renders cards. Detection lands here next.

## What it does not do

It does not know about students, classes or answers. Spring Boot owns those.
This service takes a marker id and gives back a picture; it takes a frame and
will give back marker ids and rotations. Mapping a marker to a student, or a
rotation to an answer, happens in Spring.

## Run it

```powershell
cd C:\Users\jaya\Desktop\Pythogoran\pythogorean_vision_layer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Interactive docs: http://localhost:8000/docs
Health check:     http://localhost:8000/health
A card:           http://localhost:8000/cards/7.png?label=Priya%20Sharma

## The card

A square white card with the ArUco marker in the middle and A, B, C, D printed
at the four edges. Each letter is rotated so that it reads upright when its own
edge is at the top. The student turns the card until their answer is the right
way up.

Verified mapping, measured from the generated image with
`cv2.aruco.ArucoDetector`, where the angle is the direction of the marker's top
edge (corner 0 to corner 1):

| Card rotation | Letter upright at top | Top edge angle |
|---------------|-----------------------|----------------|
| as printed    | A                     | 0              |
| 90 CCW        | B                     | 270            |
| 180           | C                     | 180            |
| 270 CCW       | D                     | 90             |

That table is the contract the detector must reproduce. It lives here because
it is a property of how the card is drawn, but the rotation to letter mapping
is applied in Spring Boot.

## Dictionary

Default `DICT_4X4_250`, giving marker ids 0 to 249. Override with the
`PYTHOGOREAN_ARUCO_DICTIONARY` environment variable, and card size with
`PYTHOGOREAN_CARD_SIZE`.

Choose the dictionary once and never change it. Every printed card in the
school is tied to it, and the dictionary a card was made with is recorded
against that card in the database. A 4x4 dictionary packs more ids into fewer
bits, so markers stay readable at smaller print sizes but are easier to confuse
at distance; a 6x6 dictionary is the other way round. Settle this by testing
with a real camera at the back of a real classroom before printing a set.
