#!/bin/bash

# Mastodon Big Data Pipeline - Quick Start
# No API keys needed - Mastodon is completely open!

set -e

echo "🐘 Mastodon Big Data Pipeline - Quick Start"
echo "============================================"
echo ""

# Check if Docker is running
echo "📋 Step 1: Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Clean up old containers
echo "📋 Step 2: Cleaning up old containers..."
docker-compose down -v > /dev/null 2>&1 || true
echo "✅ Cleanup complete"
echo ""

# Build and start services
echo "📋 Step 3: Building and starting services..."
echo "   This may take 5-10 minutes on first run..."
docker-compose up -d --build

echo ""
echo "📋 Step 4: Waiting for services to initialize..."
echo "   Waiting 30 seconds for Cassandra..."
sleep 30

# Check service status
echo ""
echo "📋 Step 5: Service status:"
docker-compose ps
echo ""

# Wait for Cassandra init
echo "📋 Step 6: Verifying Cassandra schema..."
timeout=60
counter=0
until docker logs cassandra-init 2>&1 | grep -q "Tables créées avec succès" || [ $counter -eq $timeout ]; do
    sleep 1
    ((counter++))
done

if [ $counter -eq $timeout ]; then
    echo "⚠️  Cassandra initialization timeout - check logs manually"
else
    echo "✅ Cassandra schema created"
fi
echo ""

# Display success message
echo "============================================"
echo "✅ Pipeline Started Successfully!"
echo "============================================"
echo ""
echo "🐘 MASTODON STREAMING"
echo "   • Instance: mastodon.social"
echo "   • No API keys needed!"
echo "   • Streaming public timeline with crypto keywords"
echo ""
echo "📊 Access Points:"
echo "   • Airflow UI:     http://localhost:8091 (admin/admin)"
echo "   • Spark Master:   http://localhost:8083"
echo "   • Kafka:          localhost:9093"
echo "   • Cassandra:      localhost:9042"
echo "   • MongoDB:        localhost:27017"
echo ""
echo "🎯 Next Steps:"
echo "   1. Open Airflow UI: http://localhost:8091"
echo "   2. Login with admin/admin"
echo "   3. Enable and trigger 'mastodon_pipeline' DAG"
echo "   4. Watch real Mastodon posts flow through the pipeline!"
echo ""
echo "📝 Useful Commands:"
echo "   • View Mastodon logs:  docker logs airflow-webserver -f"
echo "   • View Spark logs:     docker logs spark-worker -f"
echo "   • Check Kafka topic:   docker exec -it broker kafka-console-consumer --bootstrap-server localhost:9092 --topic Mastodon_Data --from-beginning --max-messages 5"
echo "   • Query Cassandra:     docker exec -it cassandra cqlsh -e \"SELECT * FROM reddit_keyspace.reddit_posts LIMIT 10;\""
echo ""
echo "🎉 Ready to stream real data from Mastodon!"
echo ""
