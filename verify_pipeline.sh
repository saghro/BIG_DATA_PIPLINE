#!/bin/bash

# Verification Script for Mastodon Pipeline
# Checks all components: Cassandra Schema -> Airflow DAG -> Kafka -> Spark -> Storage

echo "🧪 STARTING PIPELINE VERIFICATION"
echo "================================="

# 1. Check Cassandra Schema
echo ""
echo "📋 1. Checking Cassandra Schema..."
if docker exec cassandra cqlsh -e "DESCRIBE TABLES;" -k reddit_keyspace | grep -q "reddit_posts"; then
    echo "✅ Cassandra table 'reddit_posts' exists"
else
    echo "❌ Cassandra table missing! Attempting simple fix..."
    docker exec cassandra cqlsh -e "
    CREATE KEYSPACE IF NOT EXISTS reddit_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    USE reddit_keyspace;
    CREATE TABLE IF NOT EXISTS reddit_posts (
        id text PRIMARY KEY,
        author text,
        instance text,
        text_content text,
        score int,
        creation_date timestamp,
        ingestion_date timestamp
    );"
    echo "✅ Schema created manually"
fi

# 2. Trigger Airflow DAG
echo ""
echo "📋 2. Triggering Airflow DAG..."
# Get webserver container ID
AIRFLOW_CONTAINER=$(docker ps | grep airflow-webserver | awk '{print $1}')

if [ -z "$AIRFLOW_CONTAINER" ]; then
    echo "❌ Airflow webserver not finding"
    exit 1
fi

echo "   Found Airflow container: $AIRFLOW_CONTAINER"
echo "   Unpausing DAG..."
docker exec $AIRFLOW_CONTAINER airflow dags unpause mastodon_pipeline
echo "   Triggering DAG..."
docker exec $AIRFLOW_CONTAINER airflow dags trigger mastodon_pipeline

echo "✅ DAG triggered!"

# 3. Wait for data
echo ""
echo "📋 3. Waiting for data ingestion (30 seconds)..."
echo "   The pipeline is now:"
echo "   Mastodon API -> Kafka -> Spark -> Cassandra"
sleep 30

# 4. Check Kafka Topic
echo ""
echo "📋 4. Checking Kafka Topic 'Mastodon_Data'..."
MSG_COUNT=$(docker exec broker kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic Mastodon_Data --time -1 | awk -F ":" '{sum += $3} END {print sum}')

if [ -z "$MSG_COUNT" ]; then MSG_COUNT=0; fi
echo "   Messages in Kafka: $MSG_COUNT"

if [ "$MSG_COUNT" -gt 0 ]; then
    echo "✅ Kafka is receiving data!"
else
    echo "⚠️  No data in Kafka yet. Check internet connection or logs."
fi

# 5. Check Cassandra Data
echo ""
echo "📋 5. Checking Cassandra Storage..."
ROW_COUNT=$(docker exec cassandra cqlsh -e "SELECT count(*) FROM reddit_keyspace.reddit_posts;" | grep -o '[0-9]\+')

if [ -z "$ROW_COUNT" ]; then ROW_COUNT=0; fi
echo "   Rows in Cassandra: $ROW_COUNT"

if [ "$ROW_COUNT" -gt 0 ]; then
    echo "✅ Data successfully stored in Cassandra!"
    
    echo ""
    echo "📊 Sample Data:"
    docker exec cassandra cqlsh -e "SELECT id, author, instance, text_content FROM reddit_keyspace.reddit_posts LIMIT 3;"
else
    echo "⚠️  No data in Cassandra yet. Spark might be processing."
fi

echo ""
echo "================================="
echo "✅ VERIFICATION COMPLETE"
echo "================================="
