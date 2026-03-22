"""
Mastodon Data Ingestion
Streams posts from Mastodon instances and sends to Kafka
No API approval needed - completely open!
"""

import time
import json
from typing import List
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from mastodon import Mastodon, StreamListener
from config import KAFKA_TOPIC, KAFKA_BROKER_URL, PARTITIONS, REPLICATION_FACTOR, MASTODON_INSTANCE, KEYWORDS

class MastodonKafkaListener(StreamListener):
    """
    Custom Mastodon stream listener that sends posts to Kafka
    """
    
    def __init__(self, producer, kafka_topic, keywords):
        self.producer = producer
        self.kafka_topic = kafka_topic
        self.keywords = keywords
        self.post_count = 0
    
    def on_update(self, status):
        """Called when a new post appears in the timeline"""
        try:
            # Check if post contains relevant keywords
            text = status['content']
            if not self.is_relevant(text):
                return
            
            # Extract data
            data = {
                "id": str(status['id']),
                "author": status['account']['username'],
                "instance": status['account']['acct'].split('@')[-1] if '@' in status['account']['acct'] else MASTODON_INSTANCE,
                "text": self.clean_html(text),
                "timestamp": status['created_at'].timestamp(),
                "score": status['favourites_count'] + status['reblogs_count']
            }
            
            # Send to Kafka
            self.send_to_kafka(data)
            self.post_count += 1
            
        except Exception as e:
            print(f"⚠️ Error processing post: {e}")
    
    def is_relevant(self, text: str) -> bool:
        """Check if text contains any of the keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)
    
    def clean_html(self, html_text: str) -> str:
        """Remove HTML tags from text"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html_text)
    
    def send_to_kafka(self, data):
        """Send message to Kafka"""
        try:
            self.producer.send(self.kafka_topic, value=data)
            self.producer.flush()
            print(f"📤 [{self.post_count}] Sent: {data['id']} - @{data['author']} - {data['text'][:50]}...")
        except Exception as e:
            print(f"❌ Kafka error: {e}")


class MastodonDataIngestion:
    """
    Main class for Mastodon data ingestion
    """
    
    def __init__(self, instance_url, kafka_topic, kafka_broker_url, 
                 partitions=1, replication_factor=1):
        
        self.instance_url = instance_url
        self.kafka_topic = kafka_topic
        self.kafka_broker_url = kafka_broker_url
        self.partitions = partitions
        self.replication_factor = replication_factor
        
        # Initialize Mastodon client (no auth needed for public timeline)
        print(f"🐘 Connecting to Mastodon instance: {instance_url}")
        self.mastodon = Mastodon(
            api_base_url=instance_url,
            request_timeout=30
        )
        
        # Create Kafka topic and producer
        self.create_kafka_topic()
        self.producer = self.create_kafka_producer()
        
        print("✅ Mastodon → Kafka pipeline ready!")
    
    def create_kafka_topic(self):
        """Create Kafka topic if it doesn't exist"""
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.kafka_broker_url,
                client_id='mastodon_setup_client'
            )
            
            existing_topics = admin_client.list_topics()
            
            if self.kafka_topic in existing_topics:
                print(f"✅ Topic '{self.kafka_topic}' already exists")
            else:
                topic = NewTopic(
                    name=self.kafka_topic,
                    num_partitions=self.partitions,
                    replication_factor=self.replication_factor
                )
                admin_client.create_topics(new_topics=[topic], validate_only=False)
                print(f"✅ Topic '{self.kafka_topic}' created!")
            
            admin_client.close()
            
        except NoBrokersAvailable:
            print("❌ No Kafka broker available. Check if Kafka is running.")
        except Exception as e:
            print(f"⚠️ Error creating topic: {e}")
    
    def create_kafka_producer(self):
        """Create Kafka producer"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.kafka_broker_url,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            print("✅ Kafka producer initialized")
            return producer
        except Exception as e:
            print(f"❌ Error creating Kafka producer: {e}")
            return None
    
    def stream_public_timeline(self, keywords: List[str]):
        """
        Stream posts from Mastodon public timeline
        Filters by keywords
        """
        print(f"\n🌊 Starting Mastodon stream...")
        print(f"📍 Instance: {self.instance_url}")
        print(f"🔍 Keywords: {', '.join(keywords)}")
        print(f"📤 Sending to Kafka topic: {self.kafka_topic}\n")
        
        # Create listener
        listener = MastodonKafkaListener(self.producer, self.kafka_topic, keywords)
        
        try:
            # Start streaming public timeline
            self.mastodon.stream_public(listener, run_async=False, timeout=300, reconnect_async=False)
            
        except KeyboardInterrupt:
            print("\n🛑 Stream stopped by user")
        except Exception as e:
            print(f"\n⚠️ Stream error: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
            self.stream_public_timeline(keywords)


if __name__ == "__main__":
    print("=" * 60)
    print("🐘 MASTODON DATA INGESTION")
    print("=" * 60)
    print("\nStreaming posts from Mastodon to Kafka...")
    print("No API keys needed - completely open!\n")
    
    # Import config
    from config import MASTODON_INSTANCE, KEYWORDS, KAFKA_TOPIC, KAFKA_BROKER_URL
    
    # Create ingestion pipeline
    ingestion = MastodonDataIngestion(
        instance_url=MASTODON_INSTANCE,
        kafka_topic=KAFKA_TOPIC,
        kafka_broker_url=KAFKA_BROKER_URL
    )
    
    # Start streaming
    ingestion.stream_public_timeline(KEYWORDS)
