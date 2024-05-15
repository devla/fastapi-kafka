# FastAPI-Kafka

FastAPI-Kafka is a demonstration project showcasing the integration between FastAPI and Kafka for message production and consumption. It utilizes the `confluent_kafka` module for Kafka integration and leverages the `multiprocessing` module for concurrency.

This example is built to be fast and fun, capable of generating 100k messages in just 20 seconds on a quad-core CPU with 8 processors.

Enjoy! ;)

## Overview

The project comprises two main components:
1. **Producer App**: A command-line interface (CLI) application built using the Typer module. It generates and sends messages to Kafka.
2. **Consumer App**: A FastAPI framework application that consumes messages from Kafka. It employs background tasks and a multiprocessing approach for concurrent message consumption.

## Installation

Ensure you have provided the necessary environment variables (update variables as needed).

```bash
cp .env.example .env
```

Use Docker Compose to run project:

```bash
docker compose build
docker compose up -d
```

## Usage

Access to producer service:

```bash
docker attach producer
```
hit enter twice ;)

Consumer API is available at [http://localhost:8000/docs](http://localhost:8000/docs)

## Kafka Configuration

- **Cluster Configuration**: Consists of three brokers forming the Kafka cluster.
- **Replication Factor**: Set to 3 to ensure high availability and fault tolerance.
- **Partitions**: Each topic is configured with 10 partitions for efficient data distribution and parallel processing.
- **Automatically Created Topics**: Two topics are automatically created with the `kafka-init` service.

### Accessing Kafka UI and Adminer

- **Kafka UI**: Monitor Kafka cluster health and activity at [http://localhost:8090](http://localhost:8090).
- **Adminer**: Manage received messages and other database operations with Adminer at [http://localhost:8081](http://localhost:8081).

## Dependencies

- `FastAPI`: Web framework for building APIs.
- `SQLModel`: SQL-based data modeling for Python.
- `Pydantic-Settings`: Library for managing settings with Pydantic.
- `Asyncpg`: Asynchronous PostgreSQL driver.
- `Confluent-Kafka`: Kafka integration library.
- `Typer`: Library for building CLI applications.
- `Faker`: Library for generating fake data.
- `Orjson`: Fast JSON library for Python.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).
