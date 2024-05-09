import concurrent.futures
import time
from faker import Faker
from typer import Typer, prompt, echo
from confluent_kafka import Producer
import orjson

app = Typer()
fake = Faker()

producer = Producer({'bootstrap.servers': 'kafka:29092'})

total_messages_failed = 0
total_messages_sent = 0
total_time_taken = 0

@app.command()
def run():
    start_producing = prompt("Would you like to start producing messages? (Yes/No): ", default="Yes")
    if start_producing.lower() == "yes":
        num_messages = prompt("Enter the number of messages to produce: ", type=int, default=100)
        try:
            produce_messages(num_messages)
        except KeyboardInterrupt:
            pass

    echo("Exiting...")
    shutdown()

def shutdown():
    global producer
    if producer is not None:
        producer.flush()

    echo(f"\nTotal Messages Failed: {total_messages_failed}")
    echo(f"Total Messages Sent: {total_messages_sent}")
    echo(f"Total Time Taken: {total_time_taken:.4f} seconds")

def generate_message():
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
    return orjson.dumps(message)

def delivery_callback(err, msg):
    global total_messages_failed, total_messages_sent

    if err:
        total_messages_failed += 1
        echo(f'Message delivery failed: {err}')
    else:
        total_messages_sent += 1

def send_message(message):
    producer.produce('my-topic', message, callback=delivery_callback)
    producer.poll(0)

def produce_messages(num_messages: int):
    global total_time_taken
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for _ in range(num_messages):
            message = generate_message()
            executor.submit(send_message, message)
    end_time = time.time()
    total_time_taken = end_time - start_time


if __name__ == "__main__":
    run()