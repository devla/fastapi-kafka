import os
import time
import orjson
import asyncio
from multiprocessing import Process
from confluent_kafka import Consumer
from .config import Settings
from .database import asyncSession
from .model import Message
from .logger import logging as logger

settings = Settings()
workers = []


async def process_message(msg, consumer):
    db_message = Message(key=msg.key().decode("utf-8"), value=orjson.loads(msg.value()))
    async with asyncSession() as session:
        session.add(db_message)
        await session.commit()
        if not session.dirty:
            consumer.commit(msg)
            logger.info("Message: " + msg.value().decode())


async def consume_messages(config):
    logger.info(
        "#%s - Starting consumer group=%s, topic=%s",
        os.getpid(),
        config["kafka_kwargs"]["group.id"],
        config["topic"],
    )
    consumer = Consumer(**config["kafka_kwargs"])
    consumer.subscribe([config["topic"]])

    logger.info("#%s - Waiting for message...", os.getpid())
    while True:
        if os.getppid() == 1:
            logger.info("#%s - Parent process terminated, exiting.", os.getpid())
            break  # Exit if parent process is terminated

        try:
            msg = consumer.poll(30)
            if msg is None:
                consumer.unsubscribe()
                logger.info("#%s - No more messages, exiting.", os.getpid())
                break  # Exit if no more messages
            if msg.error():
                logger.error("#%s - Consumer error: %s", os.getpid(), msg.error())
                continue

            await process_message(msg, consumer)

        except Exception:
            logger.exception("#%s - Worker terminated.", os.getpid())
            consumer.close()


def consume_loop(config):
    asyncio.run(consume_messages(config))


def start_consumer_processes(group_id, topics): # @TODO: Topics not used.
    global workers

    # @TODO: Move this all to Settings
    config = {
        "num_workers": 4,  # @TODO Load this from settings
        "num_threads": 4,  # @TODO also
        "topic": settings.KAFKA_TOPIC,
        "kafka_kwargs": {
            "bootstrap.servers": ",".join(
                [
                    settings.KAFKA_BROKER,
                ]
            ),
            "group.id": "fastapi-concurrent-consumer",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        },
    }

    if not workers:
        try:
            for _ in range(config["num_workers"]):
                process = Process(target=consume_loop, args=(config,))
                process.start()
                workers.append(process)
                logger.info("Starting worker #%s", process.pid)

            while any(p.exitcode is None for p in workers):
                time.sleep(1)  # Check every second if any worker has exited

        finally:
            for worker in workers:
                worker.terminate()  # Terminate remaining workers
            workers = []
