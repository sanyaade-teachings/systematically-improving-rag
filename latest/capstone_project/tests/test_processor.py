"""
Integration tests for the synthetic question generation processor
"""
import asyncio
import importlib.util
import instructor
import os
import pytest
import sys
from openai import AsyncOpenAI

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dataloader import WildChatDataLoader

# Load the processor module
processor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             "03_synthetic_question_generation", "processor.py")
spec = importlib.util.spec_from_file_location("processor", processor_path)
processor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(processor_module)

generate_search_queries_v1 = processor_module.generate_search_queries_v1
SearchQueries = processor_module.SearchQueries


def load_data_from_wildchat(limit=3):
    """Load real data from WildChat dataset for testing"""
    try:
        loader = WildChatDataLoader(limit=limit)
        conversations = []
        for conversation in loader.stream_conversations(
            limit=limit,
            filter_language="English",
            min_message_length=20
        ):
            conversations.append(conversation)
            if len(conversations) >= limit:
                break
        return conversations
    except Exception as e:
        print(f"Could not load real data: {e}")
        return []


@pytest.mark.asyncio
async def test_processor_with_real_data():
    """Integration test with real WildChat data and real instructor client"""
    
    # Skip if no OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        pytest.skip("No OPENAI_API_KEY found - skipping integration test")
    
    # Load real data
    conversations = load_data_from_wildchat(limit=3)
    
    if not conversations:
        pytest.skip("Could not load real WildChat data - skipping test")
    
    # Create real instructor client using the correct pattern
    openai_client = AsyncOpenAI()
    instructor_client = instructor.from_openai(openai_client)
    
    print(f"Testing with {len(conversations)} real conversations")
    
    for i, conversation in enumerate(conversations):
        print(f"\nTesting conversation {i+1}:")
        print(f"  Hash: {conversation.get('conversation_hash', 'N/A')}")
        print(f"  First message: {conversation.get('first_message', 'N/A')[:100]}...")
        
        result = await generate_search_queries_v1(
            client=instructor_client,
            conversation_id=conversation.get('conversation_hash', f'test_{i}'),
            conversation=conversation
        )
        
        # Verify the result structure
        assert isinstance(result, SearchQueries)
        assert hasattr(result, 'chain_of_thought')
        assert hasattr(result, 'queries')
        
        # Verify it has the expected number of queries
        assert len(result.queries) >= 4
        assert len(result.queries) <= 5
        
        # Verify queries are meaningful strings
        for query in result.queries:
            assert isinstance(query, str)
            assert len(query.strip()) > 5  # More than just a few characters
            assert not query.lower().startswith('query')  # Not placeholder text
        
        # Verify chain of thought exists
        assert isinstance(result.chain_of_thought, str)
        assert len(result.chain_of_thought.strip()) > 10
        
        print(f"  ✅ Generated {len(result.queries)} queries:")
        for j, query in enumerate(result.queries):
            print(f"    {j+1}. {query}")
        print(f"  💭 Chain of thought: {result.chain_of_thought[:100]}...")


@pytest.mark.asyncio
async def test_processor_with_sample_conversations():
    """Integration test with hardcoded sample conversations"""
    
    # Skip if no OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        pytest.skip("No OPENAI_API_KEY found - skipping integration test")
    
    sample_conversations = [
        {
            'conversation_hash': 'sample_css',
            'conversation': [
                {'role': 'user', 'content': 'How do I center a div in CSS using flexbox?'},
                {'role': 'assistant', 'content': 'To center a div using flexbox, you can use display: flex with justify-content: center and align-items: center on the parent container...'}
            ],
            'first_message': 'How do I center a div in CSS using flexbox?'
        },
        {
            'conversation_hash': 'sample_python',
            'conversation': [
                {'role': 'user', 'content': 'What is the difference between Python lists and tuples? When should I use each?'},
                {'role': 'assistant', 'content': 'Lists and tuples are both sequence types in Python, but they have key differences: Lists are mutable (can be changed after creation) while tuples are immutable...'}
            ],
            'first_message': 'What is the difference between Python lists and tuples? When should I use each?'
        },
        {
            'conversation_hash': 'sample_async',
            'conversation': [
                {'role': 'user', 'content': 'How do I handle async/await in Python? I keep getting RuntimeError: This event loop is already running'},
                {'role': 'assistant', 'content': 'This error typically occurs when you try to run asyncio.run() within an already running event loop, such as in Jupyter notebooks...'}
            ],
            'first_message': 'How do I handle async/await in Python? I keep getting RuntimeError: This event loop is already running'
        }
    ]
    
    # Create real instructor client using the correct pattern
    openai_client = AsyncOpenAI()
    instructor_client = instructor.from_openai(openai_client)
    
    print(f"Testing with {len(sample_conversations)} sample conversations")
    
    for i, conversation in enumerate(sample_conversations):
        print(f"\nTesting sample conversation {i+1}: {conversation['conversation_hash']}")
        print(f"  Topic: {conversation['first_message'][:60]}...")
        
        result = await generate_search_queries_v1(
            client=instructor_client,
            conversation_id=conversation['conversation_hash'],
            conversation=conversation
        )
        
        # Verify structure and quality
        assert isinstance(result, SearchQueries)
        assert len(result.queries) >= 4
        assert len(result.queries) <= 5
        
        # Check that queries are diverse and relevant
        unique_queries = set(result.queries)
        assert len(unique_queries) == len(result.queries), "Queries should be unique"
        
        # Check that queries contain relevant keywords from the original question
        first_message_lower = conversation['first_message'].lower()
        relevant_keywords = []
        if 'css' in first_message_lower or 'div' in first_message_lower:
            relevant_keywords.extend(['css', 'center', 'div', 'flexbox'])
        elif 'python' in first_message_lower and ('list' in first_message_lower or 'tuple' in first_message_lower):
            relevant_keywords.extend(['python', 'list', 'tuple', 'difference'])
        elif 'async' in first_message_lower or 'await' in first_message_lower:
            relevant_keywords.extend(['async', 'await', 'python', 'event', 'loop'])
        
        # At least some queries should contain relevant keywords
        queries_text = ' '.join(result.queries).lower()
        keyword_matches = sum(1 for keyword in relevant_keywords if keyword in queries_text)
        assert keyword_matches > 0, f"Expected some queries to contain relevant keywords: {relevant_keywords}"
        
        print("  ✅ Generated diverse queries:")
        for j, query in enumerate(result.queries):
            print(f"    {j+1}. {query}")
        print(f"  💭 Reasoning: {result.chain_of_thought[:100]}...")


def test_load_data_integration():
    """Integration test for data loading"""
    
    conversations = load_data_from_wildchat(limit=3)
    
    if conversations:
        print(f"Successfully loaded {len(conversations)} conversations from WildChat:")
        for i, conv in enumerate(conversations):
            print(f"  {i+1}. {conv.get('conversation_hash', 'No hash')[:20]}...")
            print(f"     Message: {conv.get('first_message', 'No message')[:80]}...")
            print(f"     Language: {conv.get('language', 'Unknown')}")
            print(f"     Model: {conv.get('model', 'Unknown')}")
        
        # Verify data structure
        for conv in conversations:
            assert 'conversation' in conv
            assert isinstance(conv['conversation'], list)
            assert len(conv['conversation']) > 0
            assert 'conversation_hash' in conv
            assert 'first_message' in conv
            
        print("  ✅ Data structure validation passed")
            
    else:
        print("Could not load any conversations - check WildChat dataset access")


if __name__ == "__main__":
    # Run integration tests directly
    print("=== Integration Tests for Synthetic Question Generation ===\n")
    
    print("1. Testing data loading...")
    test_load_data_integration()
    
    if os.getenv('OPENAI_API_KEY'):
        print("\n2. Testing processor with real data...")
        asyncio.run(test_processor_with_real_data())
        
        print("\n3. Testing processor with sample conversations...")
        asyncio.run(test_processor_with_sample_conversations())
    else:
        print("\n⚠️  Skipping API tests - no OPENAI_API_KEY found")
        print("   Set OPENAI_API_KEY environment variable to run full integration tests")
    
    print("\n✅ All integration tests completed!") 