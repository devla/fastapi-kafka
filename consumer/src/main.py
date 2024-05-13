from fastapi import FastAPI, BackgroundTasks
from .kafka import start_consumer_processes
from .config import Settings
from .database import create_tables

settings = Settings()
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await create_tables()


@app.get("/start_consumers")
async def start_consumers(background_tasks: BackgroundTasks):
    background_tasks.add_task(start_consumer_processes)
    return {"message": "Kafka consumer processes started."}


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(
        app,
        proxy_headers=True,
        host="0.0.0.0",
        port=8000,
        lifespan="on",
        reload=True,
        reload_dirs=[f"{os.getcwd()}/src"],
        reload_exclude=[f"{os.getcwd()}/venv/*"],
    )
