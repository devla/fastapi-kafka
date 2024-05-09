import asyncio
from typer import Typer, prompt, echo
from faker import Faker
from aiokafka import AIOKafkaProducer
import orjson
import time

app = Typer()
fake = Faker()

producer = None
total_messages_sent = 0
total_time_taken = 0


@app.command()
async def run_async():
    await start()

async def start():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers='kafka:29092'
    )
    await producer.start()
    start_producing = prompt("Would you like to start producing messages? (Yes/No): ", default="Yes")
    if start_producing.lower() == "yes":
        num_messages = prompt("Enter the number of messages to produce: ", type=int, default=100)
        try:
            await produce_messages(num_messages)
        except KeyboardInterrupt:
            pass

    echo("Exiting...")
    await shutdown()

async def shutdown():
    global producer
    if producer is not None:
        await producer.stop()
    echo(f"Total Messages Sent: {total_messages_sent}")
    echo(f"Total Time Taken: {total_time_taken:.4f} seconds")

async def generate_and_send_message():
    global total_messages_sent, total_time_taken
    start_time = time.time()
    message = {
        'name': fake.name(),
        'email': fake.email(),
        'address': fake.address(),
        'timestamp': fake.date_time().isoformat(),
        'date': fake.date(),
        'time': fake.time(),
        'age': fake.random_int(min=18, max=65),
        'price': fake.random_element(elements=(100, 99.99, '49.99')),
        'description': fake.text(),
        'title': fake.catch_phrase(),
        'category': fake.random_element(elements=('Books', 'Electronics', 'Clothing')),
        'latitude': str(fake.latitude()),
        'longitude': str(fake.longitude()),
        'is_active': fake.random_element(elements=(True, False)),
        'is_completed': fake.random_element(elements=(1, 0)),
        'status': fake.random_element(elements=('pending', 'in progress', 'completed'))
    }
    await producer.send_and_wait('my-topic', orjson.dumps(message))
    end_time = time.time()
    time_taken = end_time - start_time
    total_time_taken += time_taken
    total_messages_sent += 1

async def produce_messages(num_messages: int):
    for _ in range(num_messages):
        await generate_and_send_message()

async def run_async_wrapper():
    await run_async()


if __name__ == "__main__":
    asyncio.run(run_async_wrapper())
