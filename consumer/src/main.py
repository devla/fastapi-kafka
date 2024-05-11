from fastapi import FastAPI, BackgroundTasks
from .kafka import consumer, start_kafka_consumer
from .config import Settings
from .database import create_tables

settings = Settings()
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await create_tables()
    consumer.subscribe([settings.KAFKA_TOPIC])


@app.on_event("shutdown")
async def shutdown_event():
    consumer.close()


# FastAPI endpoint to trigger Kafka consumption
@app.get("/consume-messages/")
async def consume_messages(background_tasks: BackgroundTasks):
    start_kafka_consumer(background_tasks)
    return {"message": "Kafka consumption triggered!"}


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
        reload_exclude=[f"{os.getcwd()}/venv/*"]
    )
