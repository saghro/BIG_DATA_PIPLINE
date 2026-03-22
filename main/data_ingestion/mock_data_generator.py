"""
Mock Reddit Data Generator
Generates fake Reddit data for testing the pipeline without real API credentials
"""

import json
import time
import random
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable

# Configuration
KAFKA_BROKER_URL = "broker:9092"
# IMPORTANT : pour tester le pipeline complet avec Spark,
# on envoie les données mock sur le même topic que celui
# consommé par Spark dans spark/config.py ("Mastodon_Data").
KAFKA_TOPIC = "Mastodon_Data"

# Sample data
SUBREDDITS = ["cryptocurrency", "Bitcoin", "ethereum", "CryptoMarkets", "dogecoin"]
AUTHORS = ["crypto_trader", "hodler123", "moon_boy", "btc_whale", "eth_fan"]
KEYWORDS = ["bitcoin", "ethereum", "crypto", "blockchain", "defi", "nft", "hodl", "moon"]

SAMPLE_TEXTS = [
    "Bitcoin is looking bullish today! 🚀",
    "Just bought more ethereum, feeling good about this investment",
    "The crypto market is volatile but I'm holding strong",
    "DeFi is the future of finance, change my mind",
    "NFTs are revolutionizing digital art",
    "Blockchain technology will change everything",
    "HODL! Don't sell during the dip",
    "To the moon! 🌙",
    "This cryptocurrency has huge potential",
    "Smart contracts are amazing technology",
]

def create_kafka_topic():
    """Create Kafka topic if it doesn't exist"""
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BROKER_URL,
            client_id='mock_data_setup'
        )
        
        existing_topics = admin_client.list_topics()
        
        if KAFKA_TOPIC in existing_topics:
            print(f"✅ Topic '{KAFKA_TOPIC}' already exists")
        else:
            topic = NewTopic(
                name=KAFKA_TOPIC,
                num_partitions=3,
                replication_factor=1
            )
            admin_client.create_topics(new_topics=[topic], validate_only=False)
            print(f"✅ Topic '{KAFKA_TOPIC}' created successfully!")
        
        admin_client.close()
        
    except NoBrokersAvailable:
        print("❌ No Kafka broker available. Make sure Kafka is running.")
        return False
    except Exception as e:
        print(f"⚠️ Error creating topic: {e}")
        return False
    
    return True

def generate_mock_post():
    """Generate a fake Reddit post"""
    return {
        "id": f"mock_{int(time.time())}_{random.randint(1000, 9999)}",
        "author": random.choice(AUTHORS),
        "subreddit": random.choice(SUBREDDITS),
        "text": random.choice(SAMPLE_TEXTS),
        "timestamp": time.time(),
        "score": random.randint(1, 100)
    }

def send_mock_data(num_posts=50, delay=2):
    """Send mock Reddit data to Kafka"""
    
    # Create topic first
    if not create_kafka_topic():
        return
    
    # Create producer
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("✅ Kafka producer initialized")
    except Exception as e:
        print(f"❌ Error creating Kafka producer: {e}")
        return
    
    print(f"\n🚀 Starting to send {num_posts} mock Reddit posts...")
    print(f"⏱️  Delay between posts: {delay} seconds\n")
    
    try:
        for i in range(num_posts):
            post = generate_mock_post()
            producer.send(KAFKA_TOPIC, value=post)
            producer.flush()
            
            print(f"📤 [{i+1}/{num_posts}] Sent: {post['id']} - {post['subreddit']} - {post['text'][:50]}...")
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        producer.close()
        print("\n✅ Mock data generation completed!")

if __name__ == "__main__":
    print("=" * 60)
    print("🎭 MOCK REDDIT DATA GENERATOR")
    print("=" * 60)
    print("\nThis script generates fake Reddit data for testing")
    print("the pipeline without needing real Reddit API credentials.\n")
    
    # Generate 50 posts with 2 seconds delay
    send_mock_data(num_posts=50, delay=2)
