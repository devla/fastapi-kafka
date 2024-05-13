#!/bin/bash

# Remove leading and trailing double quotes and split by ', ' to get individual topics
topics=$(echo $KAFKA_TOPICS | tr -d '[]" ' | tr ',' '\n')

# Remove leading and trailing square brackets from KAFKA_BROKERS
BROKERS=${KAFKA_BROKERS#[}
BROKERS=${BROKERS%]}

# Remove double quotes from the broker addresses
BROKERS=$(sed 's/"//g' <<< "$BROKERS")

# Split the string into an array using comma as the delimiter
IFS=',' read -ra BROKERS_ARRAY <<< "$BROKERS"

# Extract the first broker address
FIRST_BROKER=${BROKERS_ARRAY[0]}

# Loop over each topic
for topic in $topics; do
    kafka-topics --bootstrap-server $FIRST_BROKER --create --if-not-exists --topic "$topic" --replication-factor $KAFKA_REPLICATION_FACTOR --partitions $KAFKA_PARTITIONS
done
