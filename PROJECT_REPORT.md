# 🚀 Reddit Real-Time Sentiment & Virality Pipeline - Detailed Project Report

## 1. Project Overview
This project is an end-to-end Big Data Engineering pipeline designed to monitor, analyze, and visualize financial discussions on Reddit in real-time. It focuses on subreddits like `r/Bitcoin` and `r/CryptoCurrency` to detect viral trends and sentiment shifts.

The system performs:
- **Real-time Data Ingestion**: Fetching live posts from Reddit.
- **Sentiment Analysis**: Analyzing the emotion of the text (Positive/Negative/Neutral) using deep learning.
- **Virality Prediction**: Predicting if a post will become "HOT" based on early engagement.
- **Storage**: Saving processed data to a scalable database.
- **Visualization**: Displaying insights on a dashboard.

## 2. Technical Architecture
The project uses a modern, containerized microservices architecture orchestrated by **Docker Compose**.

### Key Components:
1.  **Ingestion Layer (Kafka)**
    - **Apache Kafka**: Acts as the central event bus. Data from Reddit is published to Kafka topics.
    - **Producers**: Python scripts (orchestrated by Airflow) fetch data from Reddit using `PRAW` and push it to Kafka.

2.  **Processing Layer (Spark & FastAPI)**
    - **Apache Spark (Structured Streaming)**: Consumes data from Kafka. It handles the "Heavy Lifting" – data transformation, aggregation, and calling external models.
    - **FastAPI (Sentiment Service)**: A dedicated microservice running a Transformer model (`mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis`). Spark sends text to this API and receives sentiment scores, decoupling heavy ML inference from the Spark cluster.
    - **Spark ML**: Runs local models for Virality Prediction (Random Forest) and Topic Modeling (LDA).

3.  **Storage Layer (Cassandra & MongoDB)**
    - **Apache Cassandra**: The *primary* storage sink. Chosen for its high write throughput and scalability for time-series data.
    - **MongoDB**: The *fallback* storage. If Cassandra is down or overwhelmed, the system automatically switches to MongoDB to ensure **Zero Data Loss**.

4.  **Orchestration (Airflow)**
    - **Apache Airflow**: Manages the workflow. It schedules the scraping tasks and ensures the pipeline runs continuously.

## 3. Data Flow
1.  **Reddit API** -> **Airflow Task**: A script fetches new posts.
2.  **Airflow Task** -> **Kafka**: Raw posts are sent to a Kafka topic.
3.  **Kafka** -> **Spark Streaming**: Spark reads the stream.
4.  **Spark** -> **FastAPI**: Spark sends post content to the Sentiment API.
5.  **FastAPI** -> **Spark**: Sentiment labels are returned.
6.  **Spark** -> **Spark ML**: Virality score and topics are calculated.
7.  **Spark** -> **Cassandra**: Enriched data is saved. (Fallback to MongoDB if failed).
8.  **Cassandra** -> **Power BI**: Dashboard reads data for visualization.

## 4. How to Run the Project

### Prerequisites
- Docker & Docker Compose installed and running.
- 4GB+ RAM available for containers.

### Steps
1.  **Start Services**:
    Run the following command in the project root:
    ```bash
    docker-compose up -d --build
    ```
    This will start Zookeeper, Kafka, Cassandra, Spark Master/Worker, Sentiment API, and Airflow.

2.  **Initialize Database**:
    The `cassandra-init` service in docker-compose is designed to automatically wait for Cassandra to be ready and then run the `init.cql` script to create the necessary keyspace and tables.

3.  **Access Interfaces**:
    - **Airflow UI**: `http://localhost:8091` (Login: `admin`/`admin`) -> Enable the DAGs to start ingestion.
    - **Spark Master**: `http://localhost:8083`
    - **Sentiment API Docs**: `http://localhost:8000/docs`

4.  **Stop Services**:
    ```bash
    docker-compose down
    ```

## 5. Directory Structure
- `main/`: Core application logic (Spark jobs, Python scripts).
- `airflow/`: Airflow DAGs and configurations.
- `distilbert_fin/`: Dockerfile and code for the Sentiment Analysis FastAPI service.
- `docker-compose.yml`: Definition of all services and networks.
- `init.cql`: Cassandra schema initialization script.

---
*Created by Antigravity Assistant*
