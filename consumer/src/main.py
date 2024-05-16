from fastapi import FastAPI, BackgroundTasks
from kafka import start_consumer_processes
from database import create_uuid_ossp_extension, create_tables
from logger import logging as logger

app = FastAPI()


async def startup_event():
    try:
        await create_uuid_ossp_extension()
        await create_tables()
    except Exception as e:
        logger.exception("Error during startup event: %s", e)


@app.get("/start_consumers")
async def start_consumers(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(start_consumer_processes)
        return {"message": "Kafka consumer processes started."}
    except Exception as e:
        logger.exception("Error starting consumer processes: %s", e)
        return {"message": "Failed to start Kafka consumer processes.", "error": str(e)}


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
        logger.info("KeyboardInterrupt: Shutting down gracefully...")
