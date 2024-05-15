import sys
import time
import orjson
from faker import Faker
from typer import Typer, prompt
from multiprocessing import Pool
from confluent_kafka import Producer
from config import get_settings

app = Typer()
faker = Faker()
settings = get_settings()

producer = Producer(**settings.KAFKA_CONFIG["kafka_kwargs"])

total_messages_failed = 0
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


def delivery_callback(err, msg):
    global total_messages_failed
    if err is not None:
        total_messages_failed += 1
        print("Failed to deliver message with error: %s" % (str(err)))


def send_messages(messages):
    global chunk, producer, total_messages_failed
    try:
        for message in messages:
            producer.produce(
                settings.KAFKA_TOPICS[0], value=message, callback=delivery_callback
            )
        producer.poll(1)
        print(f"Message chunk: {chunk} sent successfully")
        chunk += 1
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def produce_messages(num_messages: int, batch_size: int):
    global total_time_taken
    start_time = time.time()
    with Pool(processes=settings.KAFKA_NUM_WORKERS) as pool:
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
            report(num_messages)
    else:
        print("Exiting...")
        sys.exit()

    print("\n\nRe-running...")
    run()


def report(num_messages):
    print(f"\nTotal Messages Failed: {total_messages_failed}")
    print(f"Total Messages Sent: {num_messages - total_messages_failed}")
    print(f"Total Time Taken: {total_time_taken:.4f} seconds")
    reset_counters()


def reset_counters():
    global chunk, total_messages_failed, total_time_taken
    total_messages_failed = 0
    total_time_taken = 0
    chunk = 1


if __name__ == "__main__":
    app()
