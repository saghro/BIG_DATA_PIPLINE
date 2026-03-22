# REDDIT STREAMING PIPELINE - CASSANDRA SCHEMA
# Simplified schema for Reddit data without ML features

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
);