import uvicorn
from typing import Annotated
from fastapi import FastAPI, Depends
from sqlmodel import Session
from .config import Settings, get_settings
from .database import get_async_session

app = FastAPI()
settings = get_settings()


@app.get("/heros/")
async def get_heros(
    *,
    session: Session = Depends(get_async_session),
    settings: Annotated[Settings, Depends(get_settings)]
):
    return {
        "session": str(session),
        "settings": settings,
    }


if __name__ == "__main__":
    uvicorn.run(app)
