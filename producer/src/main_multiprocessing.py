import time
from faker import Faker
from typer import Typer, prompt, echo
from multiprocessing import Pool
from confluent_kafka import Producer
import orjson

app = Typer()
fake = Faker()

producer = Producer({'bootstrap.servers': 'kafka:29092'})

total_messages_failed = 0
total_messages_sent = 0
total_time_taken = 0

def generate_message(_):
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

def send_messages(messages):
    global producer
    try:
        for message in messages:
            producer.produce('my-topic', message)
        producer.flush()
        return True
    except Exception as e:
        echo(f"Error sending messages: {e}")
        return False

def produce_messages(num_messages: int, batch_size: int):
    global total_messages_failed, total_messages_sent, total_time_taken
    start_time = time.time()
    with Pool(processes=4) as pool:
        for _ in range(0, num_messages, batch_size):
            messages = pool.map(generate_message, range(batch_size))
            send_messages(messages)
            total_messages_sent += batch_size
    end_time = time.time()
    total_time_taken = end_time - start_time

@app.command()
def run():
    start_producing = prompt("Would you like to start producing messages? (Yes/No): ", default="Yes")
    if start_producing.lower() == "yes":
        num_messages = prompt("Enter the number of messages to produce: ", type=int, default=100)
        batch_size = prompt("Enter the batch size: ", type=int, default=10)
        try:
            produce_messages(num_messages, batch_size)
        except KeyboardInterrupt:
            pass

    echo("Exiting...")
    shutdown()

def shutdown():
    global total_messages_failed, total_messages_sent, total_time_taken
    echo(f"\nTotal Messages Failed: {total_messages_failed}")
    echo(f"Total Messages Sent: {total_messages_sent}")
    echo(f"Total Time Taken: {total_time_taken:.4f} seconds")

if __name__ == "__main__":
    app()
