import asyncio
import orjson
from fastapi import BackgroundTasks
from confluent_kafka import Consumer, KafkaError, KafkaException
from .config import get_settings
from .model import Message
from .database import asyncSession

settings = get_settings()
consumer = Consumer(
    {
        "bootstrap.servers": settings.KAFKA_BROKER,
        "group.id": "fastapi-consumer",
        "enable.auto.commit": "false",
        "auto.offset.reset": "earliest",
    }
)


async def process_message(msg):
    db_message = Message(key=msg.key().decode("utf-8"), value=orjson.loads(msg.value()))
    async with asyncSession() as session:
        session.add(db_message)
        await session.commit()


async def consume_messages():
    msg_count = 0
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            break
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(
                    f"%% {msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}"
                )
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            await process_message(msg)
            consumer.commit(asynchronous=True)
            msg_count += 1
            if msg_count >= settings.MSG_COUNT:
                break


async def consume_loop():
    background_task = asyncio.create_task(consume_messages())
    await background_task


def start_kafka_consumer(background_tasks: BackgroundTasks):
    background_tasks.add_task(consume_loop)
