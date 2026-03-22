from engine import RedditInferenceEngine

if __name__ == "__main__":
    print("🚀 Starting Mastodon Streaming Engine...")
    
    # Create and run the streaming engine
    engine = RedditInferenceEngine()
    engine.run()