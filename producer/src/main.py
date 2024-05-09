import os
import sys
import time
from faker import Faker
from typer import Typer, prompt, echo
from multiprocessing import Pool
from confluent_kafka import Producer
import orjson

app = Typer()
faker = Faker()

producer = Producer({"bootstrap.servers": "kafka:29092"})
num_cores_to_use = max(os.cpu_count() - 1, 1)

total_messages_failed = 0
total_messages_sent = 0
total_time_taken = 0
chunk = 1


def generate_message(_):
    message = {
        "name": faker.name(),
        "email": faker.email(),
        "address": faker.address(),
        "timestamp": faker.date_time().isoformat(),
        "date": faker.date(),
        "time": faker.time(),
        "age": faker.random_int(min=18, max=65),
        "price": faker.random_element(elements=(100, 99.99, "49.99")),
        "description": faker.text(),
        "title": faker.catch_phrase(),
        "category": faker.random_element(elements=("Books", "Electronics", "Clothing")),
        "latitude": str(faker.latitude()),
        "longitude": str(faker.longitude()),
        "is_active": faker.random_element(elements=(True, False)),
        "is_completed": faker.random_element(elements=(1, 0)),
        "status": faker.random_element(
            elements=("pending", "in progress", "completed")
        ),
    }
    return orjson.dumps(message)


def send_messages(messages):
    global chunk, producer, total_messages_failed, total_messages_sent
    try:
        for message in messages:
            producer.produce("my-topic", message)
        producer.flush()
        echo(f"Message sent successfully | Chunk: {chunk})")
        chunk += 1
        total_messages_sent += len(messages)
        return True
    except Exception as e:
        echo(f"Error sending message: {e}")
        total_messages_failed += len(messages)
        return False


def produce_messages(num_messages: int, batch_size: int):
    global total_time_taken
    start_time = time.time()
    with Pool(processes=num_cores_to_use) as pool:
        for _ in range(0, num_messages, batch_size):
            messages = pool.map(generate_message, range(batch_size))
            send_messages(messages)
    end_time = time.time()
    total_time_taken = end_time - start_time


@app.command()
def run():
    start_producing = prompt(
        "Would you like to start producing messages? (Yes/No): ", default="Yes"
    )
    if start_producing.lower() == "yes":
        num_messages = prompt(
            "Enter the number of messages to produce: ", type=int, default=100
        )
        batch_size = prompt("Enter the batch size: ", type=int, default=10)
        try:
            produce_messages(num_messages, batch_size)
        except KeyboardInterrupt:
            pass
        finally:
            report()
    else:
        echo("Exiting...")
        sys.exit()

    echo("\n\nRe-running...")
    run()


def report():
    echo(f"\nTotal Messages Failed: {total_messages_failed}")
    echo(f"Total Messages Sent: {total_messages_sent}")
    echo(f"Total Time Taken: {total_time_taken:.4f} seconds")
    reset_counters()


def reset_counters():
    global chunk, total_messages_failed, total_messages_sent, total_time_taken
    total_messages_failed = 0
    total_messages_sent = 0
    total_time_taken = 0
    chunk = 1


if __name__ == "__main__":
    app()
