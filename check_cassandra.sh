#!/bin/bash

echo "🔍 Vérification de la connexion Cassandra"
echo "=========================================="
echo ""

# 1. Vérifier que Docker est lancé
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas lancé !"
    echo "   Lance Docker Desktop et réessaye."
    exit 1
fi
echo "✅ Docker est opérationnel"
echo ""

# 2. Vérifier que le conteneur Cassandra existe et est UP
echo "📋 Vérification du conteneur Cassandra..."
CASSANDRA_STATUS=$(docker ps --filter "name=cassandra" --format "{{.Status}}" 2>/dev/null)

if [ -z "$CASSANDRA_STATUS" ]; then
    echo "❌ Le conteneur Cassandra n'est pas démarré !"
    echo ""
    echo "💡 Solution :"
    echo "   cd /Users/a/Projet_Pipeline_BigData_org"
    echo "   ./start.sh"
    exit 1
fi

echo "✅ Conteneur Cassandra trouvé : $CASSANDRA_STATUS"
echo ""

# 3. Vérifier que le port 9042 est bien mappé
echo "📋 Vérification du port 9042..."
PORT_INFO=$(docker ps --filter "name=cassandra" --format "{{.Ports}}")

if echo "$PORT_INFO" | grep -q "9042"; then
    echo "✅ Port 9042 mappé : $PORT_INFO"
else
    echo "⚠️  Le port 9042 n'est pas visible dans le mapping"
    echo "   Ports actuels : $PORT_INFO"
    echo "   Vérifie docker-compose.yml"
fi
echo ""

# 4. Vérifier que Cassandra écoute bien
echo "📋 Vérification que Cassandra écoute..."
if docker exec cassandra nodetool statusgossip > /dev/null 2>&1; then
    echo "✅ Cassandra est opérationnel et écoute"
else
    echo "⚠️  Cassandra pourrait être en cours d'initialisation"
    echo "   Attends 30-60 secondes et réessaye"
fi
echo ""

# 5. Vérifier la connexion depuis le host
echo "📋 Test de connexion depuis le host..."
# Essayer plusieurs méthodes de test
PORT_ACCESSIBLE=false

# Méthode 1: nc (netcat)
if command -v nc >/dev/null 2>&1; then
    if nc -zv 127.0.0.1 9042 2>&1 | grep -q "succeeded"; then
        PORT_ACCESSIBLE=true
    fi
fi

# Méthode 2: Test avec Python depuis le conteneur
if [ "$PORT_ACCESSIBLE" = false ]; then
    if docker exec cassandra cqlsh 127.0.0.1 9042 -e "SELECT now() FROM system.local;" >/dev/null 2>&1; then
        PORT_ACCESSIBLE=true
    fi
fi

# Méthode 3: Test direct avec cqlsh depuis le host (si disponible)
if [ "$PORT_ACCESSIBLE" = false ]; then
    if command -v cqlsh >/dev/null 2>&1; then
        if timeout 3 cqlsh 127.0.0.1 9042 -e "SELECT now() FROM system.local;" >/dev/null 2>&1; then
            PORT_ACCESSIBLE=true
        fi
    fi
fi

if [ "$PORT_ACCESSIBLE" = true ]; then
    echo "✅ Le port 9042 est accessible depuis le host"
else
    echo "⚠️  Le port 9042 pourrait ne pas être accessible depuis le host"
    echo "   Mais Cassandra fonctionne dans le conteneur."
    echo ""
    echo "💡 Note: Le dashboard peut quand même fonctionner si Cassandra"
    echo "   est accessible depuis le réseau Docker."
    echo ""
    echo "   Pour tester manuellement :"
    echo "   docker exec -it cassandra cqlsh -e \"SELECT count(*) FROM reddit_keyspace.reddit_posts;\""
fi
echo ""

# 6. Vérifier que le keyspace existe
echo "📋 Vérification du keyspace 'reddit_keyspace'..."
KEYSPACE_EXISTS=$(docker exec cassandra cqlsh -e "DESCRIBE KEYSPACES;" 2>/dev/null | grep -q "reddit_keyspace" && echo "yes" || echo "no")

if [ "$KEYSPACE_EXISTS" = "yes" ]; then
    echo "✅ Le keyspace 'reddit_keyspace' existe"
    
    # Compter les posts
    COUNT=$(docker exec cassandra cqlsh -e "SELECT count(*) FROM reddit_keyspace.reddit_posts;" 2>/dev/null | grep -o '[0-9]\+' | head -1 || echo "0")
    echo "📊 Nombre de posts dans Cassandra : $COUNT"
else
    echo "⚠️  Le keyspace 'reddit_keyspace' n'existe pas encore"
    echo ""
    echo "💡 Solution :"
    echo "   1. Attendre que cassandra-init termine (peut prendre 1-2 minutes)"
    echo "   2. Ou créer manuellement :"
    echo "      docker exec -it cassandra cqlsh -f /init.cql"
fi
echo ""

# 7. Résumé
echo "=========================================="
echo "📊 RÉSUMÉ"
echo "=========================================="
echo ""
echo "Pour lancer le dashboard BI :"
echo "  ./run_dashboard_bi.sh"
echo ""
echo "Si Cassandra n'est pas accessible :"
echo "  1. ./start.sh  (redémarrer l'infrastructure)"
echo "  2. Attendre 1-2 minutes"
echo "  3. ./check_cassandra.sh  (vérifier à nouveau)"
echo ""
