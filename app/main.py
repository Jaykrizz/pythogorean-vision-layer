from fastapi import FastAPI, File, HTTPException, Query, Response, UploadFile

from .cards import (
    SUPPORTED_DICTIONARIES,
    UnknownDictionaryError,
    marker_capacity,
    render_card,
)
from .config import settings
from .detect import detect_answers

app = FastAPI(title="Pythogorean Vision Layer", version="0.1.0")


@app.get("/health")
def health():
    return {
        "status": "up",
        "defaultDictionary": settings.dictionary,
        "defaultCardSize": settings.card_size,
        "capacity": marker_capacity(settings.dictionary),
        "supportedDictionaries": sorted(SUPPORTED_DICTIONARIES),
    }


@app.get("/cards/{marker_id}.png", response_class=Response)
def get_card(
    marker_id: int,
    label: str = Query(default="", max_length=60),
    dictionary: str = Query(default=None),
    size: int = Query(default=None, ge=200, le=4000),
):
    try:
        png = render_card(
            marker_id=marker_id,
            dictionary_name=dictionary or settings.dictionary,
            label=label,
            size=size or settings.card_size,
        )
    except UnknownDictionaryError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return Response(content=png, media_type="image/png")


@app.post("/detect")
async def detect(
    image: UploadFile = File(...),
    dictionary: str = Query(default=None),
):
    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Image is empty")

    try:
        answers = detect_answers(data, dictionary or settings.dictionary)
    except UnknownDictionaryError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"answers": answers}
