# 🚀 Guide Rapide - Démo Pipeline Big Data

## ⚡ Démo Express (5 minutes)

### 1️⃣ Démarrer l'infrastructure

```bash
cd /Users/a/Projet_Pipeline_BigData_org
./start.sh
```

**Attendre 2-3 minutes** que tous les services démarrent.

---

### 2️⃣ Vérifier que tout fonctionne

```bash
./check_cassandra.sh
```

**Résultat attendu :** Tout en vert ✅

---

### 3️⃣ Générer des données de test

```bash
./demo.sh
```

Ce script génère 20 posts mock et les envoie dans le pipeline.

---

### 4️⃣ Lancer le Dashboard BI

```bash
./run_dashboard_bi.sh
```

Puis ouvrir **http://localhost:8501** dans le navigateur.

---

### 5️⃣ Montrer les interfaces

| Interface | URL | Description |
|-----------|-----|-------------|
| **Dashboard BI** | http://localhost:8501 | Visualisation des données |
| **Airflow UI** | http://localhost:8091 | Orchestration (admin/admin) |
| **Spark Master** | http://localhost:8083 | Monitoring Spark |

---

## 📋 Checklist de Démo

- [ ] Docker Desktop est lancé
- [ ] `./start.sh` terminé avec succès
- [ ] `./check_cassandra.sh` affiche tout en vert
- [ ] `./demo.sh` a généré des données
- [ ] Dashboard BI affiche des données (count > 0)
- [ ] Spark UI montre des queries actives
- [ ] Airflow UI montre des runs réussis

---

## 🎯 Points Clés à Montrer

### Architecture
- **8 services Docker** en cours d'exécution
- **Kafka** comme buffer de messages
- **Spark** pour le traitement temps réel
- **Cassandra** pour le stockage principal
- **MongoDB** comme fallback automatique

### Flux de Données
1. **Ingestion** → Reddit/Mastodon → Kafka
2. **Traitement** → Kafka → Spark → Enrichissement ML
3. **Stockage** → Spark → Cassandra (ou MongoDB si échec)
4. **Visualisation** → Cassandra → Dashboard BI

### Fonctionnalités
- **Temps réel** : Traitement en streaming
- **Tolérance aux pannes** : Fallback automatique MongoDB
- **Scalabilité** : Architecture distribuée
- **Monitoring** : Interfaces pour chaque composant

---

## 🆘 En Cas de Problème

### Cassandra inaccessible
```bash
./fix_cassandra_port.sh
```

### Aucune donnée
```bash
./demo.sh  # Régénérer des données
```

### Tout redémarrer
```bash
./fix_and_start.sh
```

---

## 📚 Documentation Complète

Pour plus de détails, voir **`DOCUMENTATION_DEMO.md`**

---

**Bon courage pour ta démo ! 🎉**
