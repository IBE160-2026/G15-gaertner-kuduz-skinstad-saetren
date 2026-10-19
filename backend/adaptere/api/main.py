"""Oppstartslaget i adaptere/api. Komposisjon av adaptere skjer her (AD-2)."""

from fastapi import FastAPI

app = FastAPI(title="Turnushjelperen")


@app.get("/api/helse")
def helse() -> dict[str, str]:
    return {"status": "ok"}
