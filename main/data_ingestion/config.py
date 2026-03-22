from dotenv import load_dotenv
import os
load_dotenv()

# MASTODON CONFIGURATION (No API keys needed!)
MASTODON_INSTANCE = "https://mastodon.social"  # Popular instance with crypto discussions

KAFKA_TOPIC = "Mastodon_Data"
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "broker:9092")
PARTITIONS = 1
REPLICATION_FACTOR = 1

# Keywords to filter posts (crypto/tech related)
KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "crypto", "cryptocurrency",
    "blockchain", "defi", "nft", "web3", "solana", "cardano",
    "dogecoin", "doge", "altcoin", "trading", "hodl", "moon"
]