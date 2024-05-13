#!/bin/bash

# Remove leading and trailing double quotes and split by ', ' to get individual topics
topics=$(echo $KAFKA_TOPICS | tr -d '[]" ' | tr ',' '\n')

# Loop over each topic
for topic in $topics; do
    kafka-topics --bootstrap-server $KAFKA_BROKER --create --if-not-exists --topic "$topic" --replication-factor $KAFKA_REPLICATION_FACTOR --partitions $KAFKA_PARTITIONS
done
