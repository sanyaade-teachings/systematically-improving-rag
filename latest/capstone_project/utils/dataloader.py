"""
WildChat-1M Data Loader

This module provides efficient loading and streaming of the WildChat-1M dataset
with Pydantic models for type safety and data validation.
"""

from typing import Generator, List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from datasets import load_dataset
import logging

# Set up logging (suppress for cleaner output)
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


def format_conversation_history(conversation: List[dict]) -> str:
    """
    Format the conversation history into a readable text format
    
    Args:
        conversation: List of message dictionaries with 'content' and optionally 'role'
        
    Returns:
        Formatted conversation string
    """
    if not conversation or len(conversation) == 0:
        return ""
    
    formatted_messages = []
    
    for i, message in enumerate(conversation):
        # Extract content
        content = message.get('content', '').strip()
        if not content:
            continue
            
        # Try to determine role (user vs assistant)
        role = message.get('role', '')
        
        # If no role provided, alternate between user and assistant
        # Assume first message is from user
        if not role:
            role = 'user' if i % 2 == 0 else 'assistant'
        
        # Format the message
        role_label = "User" if role.lower() in ['user', 'human'] else "Assistant"
        formatted_messages.append(f"{role_label}: {content}")
    
    return "\n\n".join(formatted_messages)


def create_conversation_summary(conversation: List[dict]) -> str:
    """
    Create a brief summary of the conversation for better searchability
    
    Args:
        conversation: List of message dictionaries
        
    Returns:
        Summary string combining first user message and key topics
    """
    if not conversation or len(conversation) == 0:
        return ""
    
    # Get first message (user query)
    first_message = conversation[0].get('content', '').strip()
    
    # For longer conversations, add context about the interaction
    if len(conversation) > 2:
        summary = f"User Query: {first_message}\n\nThis was a {len(conversation)}-turn conversation"
        
        # Add assistant's response if available
        if len(conversation) > 1:
            assistant_response = conversation[1].get('content', '').strip()
            if assistant_response:
                summary += f" where the assistant responded: {assistant_response}"
        
        return summary
    else:
        return f"User Query: {first_message}"


class WildChatDataLoader:
    """Efficient data loader for WildChat-1M dataset"""
    
    def __init__(self, dataset_name: str = "allenai/WildChat-1M"):
        """
        Initialize the data loader
        
        Args:
            dataset_name: HuggingFace dataset identifier
        """
        self.dataset_name = dataset_name
        self.dataset = None
        
    def load_dataset(self, split: str = "train", limit: Optional[int] = None) -> None:
        """
        Load the dataset with optional limit
        
        Args:
            split: Dataset split to load
            limit: Maximum number of records to load (None for all)
        """
        if limit is not None:
            split_str = f"{split}[:{limit}]"
        else:
            split_str = split
            
        # Load dataset silently
        self.dataset = load_dataset(self.dataset_name, split=split_str)
    
    def stream_conversations(
        self, 
        limit: Optional[int] = None,
        min_message_length: int = 10,
        filter_language: Optional[str] = None,
        filter_toxic: bool = True,
        dataset_chunk_size: int = 50000
    ) -> Generator[dict, None, None]:
        """
        Stream conversations as Pydantic objects
        
        Args:
            limit: Maximum number of filtered conversations to yield
            min_message_length: Minimum character length for first message
            filter_language: Only yield conversations in this language
            filter_toxic: Skip toxic conversations if True
            dataset_chunk_size: Size of chunks to load from dataset at a time
            
        Yields:
            WildChatConversation objects
        """
        # Don't limit initial dataset loading - we need to process until we get enough filtered results
        if self.dataset is None:
            # Start with a reasonable chunk size, expand if needed
            initial_chunk = dataset_chunk_size if limit and limit < dataset_chunk_size else dataset_chunk_size
            self.load_dataset(limit=initial_chunk)
        
        count = 0
        processed = 0
        seen_hashes = set()  # Track seen conversation hashes for deduplication
        
        for record in self.dataset:
            processed += 1
            
            try:
                # Extract conversation hash for deduplication
                conversation_hash = record.get('conversation_hash')
                if not conversation_hash:
                    continue
                    
                # Skip if we've already seen this conversation hash
                if conversation_hash in seen_hashes:
                    continue
                
                # Extract first message for filtering
                first_msg = ""
                if record.get('conversation') and len(record['conversation']) > 0:
                    first_msg = record['conversation'][0].get('content', '')
                
                # Apply filters
                if len(first_msg.strip()) < min_message_length:
                    continue
                    
                if filter_language and record.get('language') != filter_language:
                    continue
                    
                if filter_toxic and record.get('toxic', False):
                    continue
                
                # Add to seen hashes to prevent future duplicates
                seen_hashes.add(conversation_hash)
                
                # Format conversation history and create summary
                original_conversation = record.get('conversation', [])
                formatted_history = format_conversation_history(original_conversation)
                conversation_summary = create_conversation_summary(original_conversation)
                
                # Create conversation object
                conversation_data = {
                    'conversation_hash': conversation_hash,
                    'model': record['model'],
                    'timestamp': record['timestamp'],
                    'conversation': record['conversation'],
                    'conversation_history': formatted_history,
                    'conversation_summary': conversation_summary,
                    'turn': record.get('turn', 1),
                    'language': record.get('language', 'Unknown'),
                    'country': record.get('country'),
                    'state': record.get('state'),
                    'toxic': record.get('toxic', False),
                    'redacted': record.get('redacted', False),
                    'hashed_ip': record.get('hashed_ip'),
                    'header': record.get('header'),
                    'conversation_length': len(record.get('conversation', [])),
                    'first_message': first_msg
                }
                
                yield conversation_data
                
                count += 1
                if limit and count >= limit:
                    break
                    
                # Silent processing - no progress logs
                    
            except Exception as e:
                # Silent error handling
                continue