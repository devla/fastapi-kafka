#/bin/bash

kafka-topics --bootstrap-server kafka:29092 --create --if-not-exists --topic $TEST_TOPIC_NAME --replication-factor $REPLICATION_FACTOR --partitions $PARTITIONS
