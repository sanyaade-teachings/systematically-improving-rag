#!/usr/bin/env python3
"""
Simple test script to verify the synthetic question generator setup
"""

import sys
from pathlib import Path
import os
import asyncio
import instructor
from openai import AsyncOpenAI
from processor import generate_search_queries_v1, generate_conversation_pattern_queries_v2, get_cache_stats

def test_imports():
    """Test that all required imports work"""
    print("🧪 Testing imports...")
    
    try:
        # Add parent utils to path
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        utils_dir = parent_dir / "utils"
        sys.path.append(str(utils_dir))
        
        from dataloader import WildChatDataLoader
        from processor import generate_search_queries_v1, SearchQueries
        import streamlit as st
        import instructor
        from openai import AsyncOpenAI
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_loading():
    """Test that data loading works"""
    print("\n📊 Testing data loading...")
    
    try:
        from dataloader import WildChatDataLoader
        
        loader = WildChatDataLoader()
        conversations = []
        
        # Try to load just 2 conversations as a test
        for conversation in loader.stream_conversations(
            limit=2,
            min_message_length=30,
            filter_language="English",
            filter_toxic=True
        ):
            conversations.append(conversation)
            if len(conversations) >= 2:
                break
        
        if conversations:
            print(f"✅ Successfully loaded {len(conversations)} test conversations")
            
            # Show sample data structure
            sample = conversations[0]
            print(f"   Sample conversation hash: {sample['conversation_hash'][:10]}...")
            print(f"   Sample first message: {sample['first_message'][:100]}...")
            print(f"   Model: {sample['model']}")
            print(f"   Language: {sample['language']}")
            return True
        else:
            print("⚠️  No conversations loaded - this might be expected on first run")
            return False
            
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False

def test_openai_setup():
    """Test OpenAI API key setup"""
    print("\n🔑 Testing OpenAI setup...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OpenAI API key is set")
        if api_key.startswith("sk-"):
            print("✅ API key format looks correct")
        else:
            print("⚠️  API key doesn't start with 'sk-' - verify it's correct")
        return True
    else:
        print("⚠️  OpenAI API key not set")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        return False

# Configure instructor with OpenAI
client = instructor.from_openai(AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))

# Example conversations for testing
EXAMPLE_CONVERSATIONS = [
    {
        "id": "medical_example",
        "conversation": [
            {
                "role": "user",
                "content": "I'm a 65-year-old male with diabetes, high blood pressure, and high cholesterol. I just had chest pain and my ECG shows signs of a heart attack. What's the biggest risk factor that caused this?"
            },
            {
                "role": "assistant", 
                "content": "I'm not a doctor, but I can provide some general information. The combination of your age, diabetes, hypertension, and dyslipidemia are all significant cardiovascular risk factors. Age is often considered one of the strongest non-modifiable risk factors, especially when combined with diabetes which greatly increases cardiovascular risk. However, you should discuss this with your cardiologist who can properly evaluate your specific case and risk factors. Please seek immediate medical attention if you're experiencing chest pain."
            }
        ]
    },
    {
        "id": "creative_roleplay",
        "conversation": [
            {
                "role": "user",
                "content": "Hey! I want to create a fantasy world where I can shift realities. Can you help me design a magical realm called Mysticon with interesting characters, maybe some romance, and epic adventures? I want something really personalized and immersive."
            },
            {
                "role": "assistant",
                "content": "I'd love to help you create Mysticon! Let me design a magical realm just for you. Welcome to Mysticon, a world where crystalline towers float among cloud cities and ancient forests hold secrets of reality-bending magic. You could be a Reality Weaver - someone who can step between dimensions. The realm has three main regions: the Ethereal Highlands where time flows differently, the Whispering Forests inhabited by shapeshifting guides, and the Nexus City where travelers from all realities gather. For romance, there's Lyra, a mysterious mage who teaches forbidden magic, or perhaps Kael, a warrior-poet from the Highland clans..."
            }
        ]
    },
    {
        "id": "technical_question",
        "conversation": [
            {
                "role": "user", 
                "content": "I'm trying to understand how copper corrosion works. Can you explain the electrochemical processes involved, especially the role of cuprous oxide formation and how formic acid affects the corrosion rate?"
            },
            {
                "role": "assistant",
                "content": "Copper corrosion involves several electrochemical processes. Initially, copper undergoes oxidation: Cu → Cu+ + e-. This forms cuprous oxide (Cu2O) in a protective layer. However, in the presence of oxygen and moisture, further oxidation occurs: Cu+ → Cu2+ + e-, leading to cupric compounds. Formic acid (HCOOH) significantly accelerates corrosion by: 1) Lowering pH, making the environment more corrosive, 2) Acting as a complexing agent for copper ions, and 3) Breaking down the protective oxide layer. The acid forms copper formate complexes, which are more soluble than oxide layers, thus removing the protective barrier and exposing fresh copper to further attack."
            }
        ]
    }
]

async def test_both_approaches():
    """Test both the old and new approaches to synthetic question generation."""
    
    print("🧪 Testing Synthetic Question Generation")
    print("=" * 60)
    
    for example in EXAMPLE_CONVERSATIONS:
        conv_id = example["id"]
        conversation = example
        
        print(f"\n📋 Testing Conversation: {conv_id}")
        print("-" * 40)
        
        # Show original conversation preview
        first_msg = conversation["conversation"][0]["content"][:100] + "..."
        print(f"Preview: {first_msg}")
        
        print(f"\n🔍 V1 Approach (Find This Conversation):")
        try:
            v1_result = await generate_search_queries_v1(client, conv_id, conversation)
            print(f"Reasoning: {v1_result.chain_of_thought[:100]}...")
            for i, query in enumerate(v1_result.queries, 1):
                print(f"  {i}. {query}")
        except Exception as e:
            print(f"  Error: {e}")
        
        print(f"\n🎯 V2 Approach (Find Similar Patterns):")
        try:
            v2_result = await generate_conversation_pattern_queries_v2(client, conv_id, conversation)
            print(f"Content Type: {v2_result.content_type}")
            print(f"User Intent: {v2_result.user_intent}")
            print(f"Reasoning: {v2_result.reasoning[:100]}...")
            print("Pattern Queries:")
            for i, query in enumerate(v2_result.pattern_queries, 1):
                print(f"  {i}. {query}")
        except Exception as e:
            print(f"  Error: {e}")
        
        print()
    
    # Show cache stats
    print("📊 Cache Statistics:")
    stats = get_cache_stats()
    print(f"  Cache entries: {stats.get('count', 'unknown')}")
    print(f"  Cache size: {stats.get('size', 'unknown')}")
    print(f"  Cache exists: {stats.get('exists', False)}")

async def compare_query_types():
    """Compare the types of queries generated by each approach."""
    
    print("\n🔄 Query Type Comparison")
    print("=" * 60)
    
    # Use the medical example for detailed comparison
    medical_conv = EXAMPLE_CONVERSATIONS[0]
    
    print("Example: Medical conversation about heart attack risk factors")
    print()
    
    v1_result = await generate_search_queries_v1(client, "medical", medical_conv)
    v2_result = await generate_conversation_pattern_queries_v2(client, "medical", medical_conv)
    
    print("📍 V1 (Specific Search) - Looking for THIS conversation:")
    for query in v1_result.queries:
        print(f"  • {query}")
    
    print(f"\n🎯 V2 (Pattern Search) - Looking for SIMILAR conversations:")
    print(f"Category: {v2_result.content_type}")
    print(f"Intent: {v2_result.user_intent}")
    for query in v2_result.pattern_queries:
        print(f"  • {query}")
    
    print(f"\n💡 Key Difference:")
    print("  V1: Helps find the exact same conversation")  
    print("  V2: Helps find conversations with similar themes/patterns")
    print("  V2 is better for research, content analysis, and understanding user behavior patterns")

def main():
    print("🔍 Synthetic Question Generator - Setup Test")
    print("=" * 50)
    
    results = []
    results.append(test_imports())
    results.append(test_data_loading())
    results.append(test_openai_setup())
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    if all(results):
        print("🎉 All tests passed! You're ready to run the Streamlit app.")
        print("\nTo start the app, run:")
        print("   python run_app.py")
    else:
        print("⚠️  Some issues found. Check the messages above.")
        print("\nYou can still try running the app, but you might encounter errors.")

if __name__ == "__main__":
    asyncio.run(test_both_approaches())
    asyncio.run(compare_query_types()) 