#!/bin/bash

# Quick Test Script - Run Pipeline with Mock Data
# This allows you to test the entire pipeline without Reddit API credentials

set -e

echo "🧪 PIPELINE TEST MODE - Using Mock Data"
echo "========================================"
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

# Stop existing containers
echo "📋 Step 2: Cleaning up old containers..."
docker-compose down -v > /dev/null 2>&1 || true
echo "✅ Cleanup complete"
echo ""

# Start services
echo "📋 Step 3: Starting services..."
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

# Run mock data generator
echo "=========================================="
echo "🎭 STARTING MOCK DATA GENERATOR"
echo "=========================================="
echo ""
echo "This will generate fake Reddit data and send it to Kafka"
echo "The Spark streaming engine will process it automatically"
echo ""

# Copy mock generator to broker container and run it
docker cp /Users/a/Projet_Pipeline_BigData_org/main/data_ingestion/mock_data_generator.py broker:/tmp/
docker exec -it broker python /tmp/mock_data_generator.py

echo ""
echo "=========================================="
echo "✅ Test Complete!"
echo "=========================================="
echo ""
echo "📊 Check Results:"
echo "   • Spark UI:     http://localhost:8083"
echo "   • Airflow UI:   http://localhost:8091 (admin/admin)"
echo ""
echo "📝 Verify Data in Cassandra:"
echo "   docker exec -it cassandra cqlsh -e \"SELECT * FROM reddit_keyspace.reddit_posts LIMIT 10;\""
echo ""
echo "📝 Verify Data in MongoDB (if Cassandra failed):"
echo "   docker exec -it mongodb mongosh --eval \"use reddit_backup_local; db.viral_posts.find().limit(5)\""
echo ""
