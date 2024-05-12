import os
import time
import orjson
import asyncio
import threading
from multiprocessing import Process
from queue import Queue
from confluent_kafka import Consumer
from .config import Settings
from .database import asyncSession
from .model import Message
from .logger import logging as logger

settings = Settings()


def _process_msg(q, c):
    async def process_message(session, msg):
        db_message = Message(key=msg.key().decode("utf-8"), value=orjson.loads(msg.value()))
        # async with session() as async_session:
        session.add(db_message)
        await session.commit()

    msg = q.get(timeout=60)  # Set timeout to care for POSIX<3.0 and Windows.
    logger.info(
        "#%sT%s - Received message: %s",
        os.getpid(),
        threading.get_ident(),
        msg.value().decode("utf-8"),
    )
    session = asyncSession()
    asyncio.run(process_message(session, msg))
    q.task_done()
    c.commit(msg) # @TODO Check if commit works, maybe without msg.


def _consume(config):
    logger.info(
        "#%s - Starting consumer group=%s, topic=%s",
        os.getpid(),
        config["kafka_kwargs"]["group.id"],
        config["topic"],
    )
    c = Consumer(**config["kafka_kwargs"])
    c.subscribe([config["topic"]])
    q = Queue(maxsize=config["num_threads"])

    while True:
        if os.getppid() == 1:
            logger.info("#%s - Parent process terminated, exiting.", os.getpid())
            break  # Exit if parent process is terminated

        logger.info("#%s - Waiting for message...", os.getpid())
        try:
            msg = c.poll(30)
            if msg is None:
                logger.info("#%s - No more messages, exiting.", os.getpid())
                break  # Exit if no more messages
            if msg.error():
                logger.error("#%s - Consumer error: %s", os.getpid(), msg.error())
                continue
            q.put(msg)
            t = threading.Thread(target=_process_msg, args=(q, c))
            t.start()
        except Exception:
            logger.exception("#%s - Worker terminated.", os.getpid())
            c.close()


def start_consumer_processes(group_id, topics):
    logger.info("start_consumer_processes start")

    config = {
        "num_workers": 4, # @TODO Load this from settings
        "num_threads": 4, # @TODO also
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

    workers = []
    try:
        for _ in range(config["num_workers"]):
            p = Process(target=_consume, args=(config,))
            p.start()
            workers.append(p)
            logger.info("Starting worker #%s", p.pid)

        while any(p.exitcode is None for p in workers):
            time.sleep(1)  # Check every second if any worker has exited

    finally:
        for worker in workers:
            worker.terminate()  # Terminate remaining workers
        logger.debug("start_consumer_processes end")
