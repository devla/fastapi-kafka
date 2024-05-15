import os
import time
import orjson
import asyncio
from multiprocessing import Process
from confluent_kafka import Consumer
from .config import get_settings
from .database import asyncSession
from .model import Message
from .logger import logging as logger

settings = get_settings()
workers = []


async def process_message(msg, consumer):
    db_message = Message(value=orjson.loads(msg.value()))
    async with asyncSession() as session:
        session.add(db_message)
        await session.commit()
        if not session.dirty:
            consumer.commit(msg)
            logger.info(
                "#%s | Message received",
                os.getpid(),
            )
        else:
            logger.info("#%s | Dirty Message: " + msg.value().decode())


async def consume_messages(config):
    logger.info(
        "#%s | Starting consumer group=%s, topics=%s",
        os.getpid(),
        config["kafka_kwargs"]["group.id"],
        config["topics"],
    )
    consumer = Consumer(**config["kafka_kwargs"])
    consumer.subscribe(config["topics"])

    logger.info("#%s | Waiting for message...", os.getpid())
    while True:
        if os.getppid() == 1:
            logger.info("#%s | Parent process terminated, exiting.", os.getpid())
            break  # Exit if parent process is terminated

        try:
            msg = consumer.poll(30)
            if msg is None:
                consumer.unsubscribe()
                logger.info("#%s | No more messages, exiting.", os.getpid())
                break  # Exit if no more messages
            if msg.error():
                logger.error("#%s | Consumer error: %s", os.getpid(), msg.error())
                continue

            await process_message(msg, consumer)

        except Exception:
            logger.exception("#%s - Worker terminated.", os.getpid())
            consumer.close()
            break


def consume_loop(config):
    asyncio.run(consume_messages(config))


def start_consumer_processes():
    global workers

    if not workers:
        try:
            for _ in range(settings.KAFKA_NUM_WORKERS):
                process = Process(target=consume_loop, args=(settings.KAFKA_CONFIG,))
                process.start()
                workers.append(process)
                logger.info("#%s | Starting worker", process.pid)

            while any(p.exitcode is None for p in workers):
                time.sleep(1)  # Check every second if any worker has exited

        finally:
            for worker in workers:
                worker.terminate()  # Terminate remaining workers
            workers = []
