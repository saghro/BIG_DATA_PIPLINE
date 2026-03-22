#!/bin/bash

# Script de Démo - Pipeline Big Data Mastodon/Reddit
# Automatise la génération de données mock et la vérification du pipeline

set -e

echo "🎬 ============================================"
echo "🎬 DÉMO PIPELINE BIG DATA"
echo "🎬 ============================================"
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Vérifier que Docker est lancé
echo -e "${BLUE}📋 Étape 1: Vérification Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas lancé !"
    echo "   Lance Docker Desktop et réessaye."
    exit 1
fi
echo -e "${GREEN}✅ Docker est opérationnel${NC}"
echo ""

# 2. Vérifier que les conteneurs sont UP
echo -e "${BLUE}📋 Étape 2: Vérification des services...${NC}"
if ! docker ps | grep -q "broker\|cassandra\|spark-master"; then
    echo "⚠️  Certains services ne sont pas lancés."
    echo "   Lance './start.sh' d'abord pour démarrer l'infrastructure."
    exit 1
fi
echo -e "${GREEN}✅ Services Docker opérationnels${NC}"
echo ""

# 3. Récupérer le conteneur Airflow
AIRFLOW_CONTAINER=$(docker ps | grep airflow-webserver | awk '{print $1}' | head -1)
if [ -z "$AIRFLOW_CONTAINER" ]; then
    echo "❌ Conteneur Airflow non trouvé !"
    exit 1
fi
echo -e "${GREEN}✅ Conteneur Airflow trouvé: ${AIRFLOW_CONTAINER}${NC}"
echo ""

# 4. Compter les posts actuels dans Cassandra
echo -e "${BLUE}📋 Étape 3: État actuel de Cassandra...${NC}"
CURRENT_COUNT=$(docker exec cassandra cqlsh -e "SELECT count(*) FROM reddit_keyspace.reddit_posts;" 2>/dev/null | grep -o '[0-9]\+' | head -1 || echo "0")
echo -e "${GREEN}📊 Posts actuels dans Cassandra: ${CURRENT_COUNT}${NC}"
echo ""

# 5. Générer des données mock pour la démo
echo -e "${BLUE}📋 Étape 4: Génération de données mock pour la démo...${NC}"
echo -e "${YELLOW}   Génération de 20 posts (rapide pour la démo)...${NC}"

docker exec -i $AIRFLOW_CONTAINER python << 'PYTHON_SCRIPT'
import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='broker:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

posts_data = [
    "Bitcoin is looking bullish today! 🚀",
    "Just bought more ethereum, feeling good about this investment",
    "The crypto market is volatile but I'm holding strong",
    "DeFi is the future of finance, change my mind",
    "NFTs are revolutionizing digital art",
    "Blockchain technology will change everything",
    "HODL! Don't sell during the dip",
    "To the moon! 🌙",
    "This cryptocurrency has huge potential",
    "Smart contracts are amazing technology"
]

authors = ['crypto_trader', 'hodler123', 'moon_boy', 'btc_whale', 'eth_fan']
subreddits = ['Bitcoin', 'ethereum', 'cryptocurrency', 'CryptoMarkets', 'dogecoin']

for i in range(20):
    post = {
        'id': f'demo_{int(time.time())}_{random.randint(1000, 9999)}',
        'author': random.choice(authors),
        'subreddit': random.choice(subreddits),
        'text': random.choice(posts_data),
        'timestamp': time.time(),
        'score': random.randint(1, 100)
    }
    producer.send('Mastodon_Data', value=post)
    producer.flush()
    print(f'📤 [{i+1}/20] Sent: {post["id"]} - {post["subreddit"]} - {post["text"][:40]}...')
    time.sleep(1)

producer.close()
print('✅ Données de démo envoyées avec succès!')
PYTHON_SCRIPT

echo ""
echo -e "${GREEN}✅ Génération terminée${NC}"
echo ""

# 6. Attendre que Spark traite les données
echo -e "${BLUE}📋 Étape 5: Attente du traitement Spark...${NC}"
echo -e "${YELLOW}   Attente de 30 secondes pour que Spark traite les données...${NC}"
for i in {30..1}; do
    echo -ne "\r   ⏳ $i secondes restantes...  "
    sleep 1
done
echo -e "\r   ✅ Traitement terminé                    "
echo ""

# 7. Vérifier les nouvelles données dans Cassandra
echo -e "${BLUE}📋 Étape 6: Vérification des résultats...${NC}"
NEW_COUNT=$(docker exec cassandra cqlsh -e "SELECT count(*) FROM reddit_keyspace.reddit_posts;" 2>/dev/null | grep -o '[0-9]\+' | head -1 || echo "0")
ADDED=$((NEW_COUNT - CURRENT_COUNT))

if [ "$ADDED" -gt 0 ]; then
    echo -e "${GREEN}✅ ${ADDED} nouveaux posts ajoutés dans Cassandra !${NC}"
    echo -e "${GREEN}📊 Total: ${NEW_COUNT} posts${NC}"
else
    echo -e "${YELLOW}⚠️  Aucun nouveau post détecté (Spark pourrait encore traiter)${NC}"
fi
echo ""

# 8. Afficher quelques exemples
echo -e "${BLUE}📋 Étape 7: Exemples de données...${NC}"
docker exec cassandra cqlsh -e "SELECT id, author, subreddit, text_content FROM reddit_keyspace.reddit_posts LIMIT 3;" 2>/dev/null | grep -v "^$" | tail -4
echo ""

# 9. Afficher les URLs utiles
echo "============================================"
echo -e "${GREEN}✅ DÉMO TERMINÉE AVEC SUCCÈS !${NC}"
echo "============================================"
echo ""
echo "📊 URLs pour la démo :"
echo "   • Dashboard Streamlit:  http://localhost:8501"
echo "   • Airflow UI:            http://localhost:8091 (admin/admin)"
echo "   • Spark Master UI:      http://localhost:8083"
echo ""
echo "📝 Commandes utiles :"
echo "   • Voir les posts:       docker exec -it cassandra cqlsh -e \"SELECT count(*) FROM reddit_keyspace.reddit_posts;\""
echo "   • Exporter CSV:         docker exec -it cassandra cqlsh -e \"COPY reddit_keyspace.reddit_posts TO 'reddit_posts.csv' WITH HEADER = TRUE;\""
echo "   • Lancer dashboard:     ./run_dashboard.sh"
echo ""
echo "🎉 Le pipeline est opérationnel et prêt pour la démo !"
echo ""
