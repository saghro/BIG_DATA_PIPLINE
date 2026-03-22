#!/bin/bash

# Script pour corriger les problèmes et démarrer le pipeline complet

set -e

echo "🔧 ============================================"
echo "🔧 CORRECTION ET DÉMARRAGE DU PIPELINE"
echo "🔧 ============================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Vérifier Docker
echo -e "${BLUE}📋 Étape 1: Vérification Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker n'est pas lancé !${NC}"
    echo ""
    echo "💡 Actions à faire :"
    echo "   1. Lance Docker Desktop depuis Applications"
    echo "   2. Attends que l'icône Docker soit verte dans la barre de menu"
    echo "   3. Relance ce script : ./fix_and_start.sh"
    exit 1
fi
echo -e "${GREEN}✅ Docker est opérationnel${NC}"
echo ""

# 2. Démarrer l'infrastructure
echo -e "${BLUE}📋 Étape 2: Démarrage de l'infrastructure...${NC}"
echo -e "${YELLOW}   Cela peut prendre 2-5 minutes...${NC}"
echo ""

cd /Users/a/Projet_Pipeline_BigData_org
./start.sh

echo ""
echo -e "${BLUE}📋 Étape 3: Attente de l'initialisation complète...${NC}"
echo -e "${YELLOW}   Attente de 60 secondes pour que tous les services soient prêts...${NC}"

for i in {60..1}; do
    echo -ne "\r   ⏳ $i secondes restantes...  "
    sleep 1
done
echo -e "\r   ✅ Attente terminée                    "
echo ""

# 3. Vérifier Cassandra
echo -e "${BLUE}📋 Étape 4: Vérification Cassandra...${NC}"
CASSANDRA_UP=$(docker ps --filter "name=cassandra" --format "{{.Status}}" | grep -q "Up" && echo "yes" || echo "no")

if [ "$CASSANDRA_UP" = "yes" ]; then
    echo -e "${GREEN}✅ Cassandra est démarré${NC}"
    
    # Vérifier que le port est accessible
    if timeout 3 bash -c "echo > /dev/tcp/127.0.0.1/9042" 2>/dev/null; then
        echo -e "${GREEN}✅ Port 9042 accessible${NC}"
    else
        echo -e "${YELLOW}⚠️  Port 9042 pas encore accessible, attente supplémentaire...${NC}"
        sleep 30
    fi
    
    # Vérifier le keyspace
    KEYSPACE_EXISTS=$(docker exec cassandra cqlsh -e "DESCRIBE KEYSPACES;" 2>/dev/null | grep -q "reddit_keyspace" && echo "yes" || echo "no")
    
    if [ "$KEYSPACE_EXISTS" = "yes" ]; then
        echo -e "${GREEN}✅ Keyspace 'reddit_keyspace' existe${NC}"
    else
        echo -e "${YELLOW}⚠️  Keyspace n'existe pas, création en cours...${NC}"
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
        );" 2>/dev/null || echo "   (Cassandra peut être encore en initialisation)"
    fi
else
    echo -e "${RED}❌ Cassandra n'est pas démarré${NC}"
    echo "   Vérifie les logs : docker logs cassandra"
    exit 1
fi
echo ""

# 4. Activer le DAG Airflow
echo -e "${BLUE}📋 Étape 5: Activation du DAG Airflow...${NC}"
AIRFLOW_CONTAINER=$(docker ps | grep airflow-webserver | awk '{print $1}' | head -1)

if [ -z "$AIRFLOW_CONTAINER" ]; then
    echo -e "${YELLOW}⚠️  Conteneur Airflow non trouvé${NC}"
else
    echo -e "${GREEN}✅ Conteneur Airflow trouvé${NC}"
    
    # Unpause le DAG
    docker exec $AIRFLOW_CONTAINER airflow dags unpause mastodon_pipeline 2>/dev/null
    echo -e "${GREEN}✅ DAG 'mastodon_pipeline' activé${NC}"
fi
echo ""

# 5. Résumé final
echo "============================================"
echo -e "${GREEN}✅ TOUT EST PRÊT !${NC}"
echo "============================================"
echo ""
echo "📊 URLs disponibles :"
echo "   • Dashboard BI:        http://localhost:8501"
echo "   • Airflow UI:           http://localhost:8091 (admin/admin)"
echo "   • Spark Master UI:      http://localhost:8083"
echo ""
echo "📝 Prochaines étapes :"
echo ""
echo "   1. Lancer le dashboard BI :"
echo "      ./run_dashboard_bi.sh"
echo ""
echo "   2. Générer des données de test :"
echo "      ./demo.sh"
echo ""
echo "   3. Vérifier que tout fonctionne :"
echo "      ./check_cassandra.sh"
echo ""
echo "🎉 Le pipeline est maintenant opérationnel !"
echo ""
