#!/bin/bash

# Script pour corriger le problème de port Cassandra

set -e

echo "🔧 Correction du port Cassandra"
echo "================================="
echo ""

# Vérifier que Docker est lancé
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas lancé !"
    exit 1
fi

echo "📋 Étape 1: Arrêt de Cassandra..."
docker stop cassandra 2>/dev/null || true
sleep 2

echo "📋 Étape 2: Suppression du conteneur..."
docker rm cassandra 2>/dev/null || true
sleep 1

echo "📋 Étape 3: Redémarrage avec docker-compose..."
cd /Users/a/Projet_Pipeline_BigData_org
docker-compose up -d cassandra

echo "📋 Étape 4: Attente de l'initialisation..."
echo "   Attente de 30 secondes..."
sleep 30

echo "📋 Étape 5: Vérification du port..."
for i in {1..10}; do
    if timeout 2 bash -c "echo > /dev/tcp/127.0.0.1/9042" 2>/dev/null; then
        echo "✅ Port 9042 accessible !"
        break
    else
        echo "   Tentative $i/10..."
        sleep 3
    fi
done

echo ""
echo "📋 Étape 6: Création du keyspace..."
docker exec cassandra cqlsh -e "
CREATE KEYSPACE IF NOT EXISTS reddit_keyspace
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS reddit_keyspace.reddit_posts (
    id TEXT PRIMARY KEY,
    author TEXT,
    subreddit TEXT,
    text_content TEXT,
    score INT,
    creation_date TIMESTAMP,
    ingestion_date TIMESTAMP
);" 2>/dev/null || echo "⚠️  Keyspace peut-être déjà créé ou Cassandra pas encore prêt"

echo ""
echo "=========================================="
echo "✅ Correction terminée !"
echo "=========================================="
echo ""
echo "Vérifie maintenant avec :"
echo "  ./check_cassandra.sh"
echo ""
