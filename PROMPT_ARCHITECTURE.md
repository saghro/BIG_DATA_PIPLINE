# 🎨 Prompt pour Générer l'Architecture du Pipeline Mastodon

## Prompt pour générer l'image d'architecture

```
Crée un diagramme d'architecture Big Data moderne et professionnel pour un pipeline de traitement de données en temps réel, avec le style suivant :

**CONTEXTE :**
Pipeline Big Data temps réel qui ingère des données depuis Mastodon (réseau social décentralisé), les traite avec Apache Spark, et les stocke dans Cassandra avec un mécanisme de fallback MongoDB.

**COMPOSANTS À INCLURE :**

1. **SOURCE DE DONNÉES :**
   - Mastodon (logo Mastodon avec icône éléphant 🐘)
   - Timeline publique Mastodon
   - Flèche pointant vers Kafka

2. **DOCKER COMPOSE ENVIRONNEMENT (grande boîte bleue avec bordure) :**
   - **Kafka** : Message broker Apache Kafka (logo Kafka)
   - **Spark Streaming** : Apache Spark avec logo Spark et étoiles
   - **Hugging Face** : Intégration pour analyse de sentiment (logo Hugging Face avec éclair)
   - **Cassandra** : Base NoSQL principale (logo Cassandra avec icône œil)
   - **MongoDB** : Base de fallback (logo MongoDB avec feuille)
   - **Airflow** : Orchestration (logo Airflow)
   - Tous les composants doivent avoir l'icône Docker (baleine)

3. **FLUX DE DONNÉES :**
   - Mastodon → Kafka (flèche simple)
   - Kafka → Spark Streaming (flèche simple)
   - Spark Streaming ↔ Hugging Face (flèche bidirectionnelle)
   - Spark Streaming → Cassandra (flèche simple, avec label "Primary Storage")
   - Spark Streaming → MongoDB (flèche simple, avec label "Fallback if Cassandra fails")
   - Airflow → Spark Streaming (flèche en pointillés, label "Orchestration")
   - Cassandra → Power BI (flèche simple)
   - MongoDB → Power BI (flèche simple)

4. **VISUALISATION :**
   - **Power BI** : Dashboard BI (logo Power BI avec graphique)
   - Reçoit les données depuis Cassandra et MongoDB

**STYLE VISUEL :**
- Fond blanc ou gris clair
- Couleurs modernes : bleu pour Kafka/Spark, vert pour Cassandra, vert pour MongoDB, orange pour Airflow
- Flèches colorées selon le type de flux
- Icônes Docker (baleine) sur tous les composants containerisés
- Labels clairs en anglais ou français
- Design épuré et professionnel
- Légende si nécessaire

**TEXTE À INCLURE :**
- "Mastodon" (pas Reddit)
- "Mastodon Timeline" ou "Public Timeline"
- "docker Compose" dans le coin supérieur droit de la boîte Docker
- "Primary Storage" au-dessus de Cassandra
- "Fallback Storage" au-dessus de MongoDB
- "Orchestration" sur la flèche Airflow
- "Real-time Processing" sur Spark Streaming
- "Sentiment Analysis" sur Hugging Face

**ORGANISATION :**
- Mastodon en haut à gauche
- Boîte Docker Compose au centre
- Power BI en bas à droite
- Flux de gauche à droite et de haut en bas
```

---

## Prompt alternatif (plus détaillé)

```
Génère un diagramme d'architecture Big Data professionnel montrant un pipeline de streaming temps réel pour l'analyse de données Mastodon.

**STRUCTURE :**

1. **COUCHE INGESTION (Gauche) :**
   - Mastodon avec logo éléphant 🐘
   - Label : "Mastodon Public Timeline"
   - Flèche vers Kafka

2. **COUCHE STREAMING (Centre-Haut) :**
   - Boîte bleue avec bordure épaisse, label "Docker Compose" en haut à droite
   - À l'intérieur :
     * Kafka (logo Apache Kafka, icône Docker)
     * Spark Streaming (logo Spark avec étoiles, icône Docker)
     * Hugging Face (logo HF avec éclair, icône Docker) - connecté bidirectionnellement à Spark
     * Airflow (logo Airflow, icône Docker) - flèche pointillée vers Spark

3. **COUCHE STOCKAGE (Centre-Bas) :**
   - Cassandra (logo Cassandra, icône Docker) - label "Primary Storage"
   - MongoDB (logo MongoDB, icône Docker) - label "Fallback Storage"
   - Flèches depuis Spark vers les deux bases

4. **COUCHE VISUALISATION (Droite) :**
   - Power BI (logo Power BI avec graphique)
   - Flèches depuis Cassandra et MongoDB

**COULEURS :**
- Kafka : Bleu foncé
- Spark : Bleu clair avec étoiles
- Cassandra : Vert/bleu
- MongoDB : Vert
- Airflow : Orange/rouge
- Power BI : Jaune/orange
- Hugging Face : Jaune avec éclair

**STYLE :**
- Design moderne et épuré
- Flèches avec labels explicites
- Icônes Docker sur tous les composants containerisés
- Fond blanc ou gris très clair
- Typographie claire et lisible
```

---

## Prompt pour outils spécifiques

### Pour Draw.io / Lucidchart

```
Crée un diagramme d'architecture avec les éléments suivants :

**FORMES ET SYMBOLES :**
- Rectangle arrondi pour Mastodon (avec icône éléphant)
- Cylindre pour Kafka
- Cercle avec étoiles pour Spark Streaming
- Nuage pour Hugging Face
- Base de données (cylindre) pour Cassandra et MongoDB
- Hexagone pour Airflow
- Graphique pour Power BI

**ORGANISATION :**
- Layout de gauche à droite
- Grouper les composants Docker dans une grande boîte bleue
- Utiliser des flèches colorées pour les flux
- Ajouter des labels sur les flèches

**COULEURS :**
- Mastodon : Violet/Mauve
- Kafka : Bleu foncé
- Spark : Bleu clair
- Cassandra : Vert
- MongoDB : Vert clair
- Airflow : Orange
- Power BI : Jaune
```

---

### Pour Mermaid / PlantUML

```
graph TB
    Mastodon[Mastodon Public Timeline 🐘] --> Kafka[Kafka Message Broker]
    Kafka --> Spark[Spark Streaming]
    Spark <--> HF[Hugging Face Sentiment]
    Spark --> Cassandra[Cassandra Primary Storage]
    Spark --> MongoDB[MongoDB Fallback Storage]
    Airflow[Airflow Orchestration] -.-> Spark
    Cassandra --> PowerBI[Power BI Dashboard]
    MongoDB --> PowerBI
    
    subgraph Docker["Docker Compose Environment"]
        Kafka
        Spark
        HF
        Cassandra
        MongoDB
        Airflow
    end
    
    style Mastodon fill:#6364FF
    style Kafka fill:#231F20
    style Spark fill:#E25A1C
    style Cassandra fill:#1287B1
    style MongoDB fill:#47A248
    style Airflow fill:#E4392C
    style PowerBI fill:#F2C811
```

---

## Instructions pour utiliser ces prompts

### Option 1 : Outil de génération d'images IA (DALL-E, Midjourney, etc.)

Copie le premier prompt et colle-le dans l'outil. Ajuste selon tes besoins.

### Option 2 : Outil de diagrammes (Draw.io, Lucidchart, etc.)

1. Ouvre Draw.io ou Lucidchart
2. Utilise le prompt "Pour Draw.io / Lucidchart"
3. Crée les formes manuellement selon les instructions
4. Ajoute les logos depuis les bibliothèques d'icônes

### Option 3 : Code Mermaid (pour documentation Markdown)

Utilise le code Mermaid fourni dans un fichier `.md` :

```markdown
```mermaid
[colle le code Mermaid ici]
```
```

---

## Résultat attendu

L'image générée doit montrer :
- ✅ Mastodon (pas Reddit) comme source de données
- ✅ Tous les composants dans une boîte "Docker Compose"
- ✅ Flux clairs entre les composants
- ✅ Labels explicites (Primary Storage, Fallback Storage, etc.)
- ✅ Icônes Docker sur les composants containerisés
- ✅ Power BI recevant les données depuis Cassandra et MongoDB

---

**Note :** Tu peux adapter ces prompts selon l'outil que tu utilises (DALL-E, Midjourney, Draw.io, Lucidchart, etc.).
