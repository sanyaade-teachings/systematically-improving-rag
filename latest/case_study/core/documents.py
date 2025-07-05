from pathlib import Path
from datasets import load_dataset
from core.db import setup_database, load_conversations_to_sqlite
import itertools


def load_wildchat_into_db(db_path: Path, limit: int = 10000):
    """Load WildChat data into database"""
    # Setup database
    setup_database(db_path)

    # Load dataset
    dataset = load_dataset("allenai/WildChat-1M", split="train", streaming=True)

    conversations = []
    count = 0

    for conv in itertools.islice(dataset, limit):
        try:
            # Extract first message for embedding
            first_message = ""
            if conv.get("conversation") and len(conv["conversation"]) > 0:
                first_message = conv["conversation"][0].get("content", "")

            conversation_data = {
                "conversation_hash": conv["conversation_hash"],
                "text": first_message,  # Just the first message for embedding
                "conversation_full": str(
                    conv["conversation"]
                ),  # Full conversation as string
                "timestamp": conv.get("timestamp"),
                "language": conv.get("language", "English"),
                "country": conv.get("country"),
            }
            conversations.append(conversation_data)
            count += 1

            if count % 100 == 0:
                print(f"Processed {count} conversations...")

        except Exception as e:
            print(f"Error processing conversation: {e}")
            continue

    # Save to database
    inserted_count = load_conversations_to_sqlite(conversations, db_path)
    print(f"Inserted {inserted_count} conversations into database")

    return conversations
