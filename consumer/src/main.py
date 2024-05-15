from fastapi import FastAPI, BackgroundTasks
from kafka import start_consumer_processes
from config import Settings
from database import create_uuid_ossp_extension, create_tables

settings = Settings()
app = FastAPI()


async def startup_event():
    await create_uuid_ossp_extension()
    await create_tables()


@app.get("/start_consumers")
async def start_consumers(background_tasks: BackgroundTasks):
    background_tasks.add_task(start_consumer_processes)
    return {"message": "Kafka consumer processes started."}


app.add_event_handler("startup", startup_event)


if __name__ == "__main__":
    import uvicorn

    try:
        uvicorn.run(
            app,
            proxy_headers=True,
            host="0.0.0.0",
            port=8000,
            lifespan="on",
        )
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Shutting down gracefully...")
