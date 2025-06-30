import streamlit as st
import asyncio
from typing import List, Dict, Any
import instructor
from openai import AsyncOpenAI
import os
from pathlib import Path
import sys

# Add the parent utils directory to the Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
utils_dir = parent_dir / "utils"
sys.path.append(str(utils_dir))

from dataloader import WildChatDataLoader
from processor import synthetic_question_generation_v1, SearchQueries, get_cache_stats, clear_cache, is_cached

# Configure Streamlit page
st.set_page_config(
    page_title="Synthetic Question Generator",
    page_icon="🔍",
    layout="wide"
)

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    """Initialize instructor-patched OpenAI client"""
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return instructor.apatch(client)

@st.cache_data
def load_conversations(limit: int = 40) -> List[Dict[str, Any]]:
    """Load conversations from WildChat dataset"""
    loader = WildChatDataLoader()
    conversations = []
    
    with st.spinner("Loading conversations from WildChat dataset..."):
        for conversation in loader.stream_conversations(
            limit=limit,
            min_message_length=50,
            filter_language="English",
            filter_toxic=True
        ):
            conversations.append(conversation)
            if len(conversations) >= limit:
                break
    
    return conversations

async def process_conversation(client, conversation_id: str, conversation: Dict[str, Any]) -> SearchQueries:
    """Generate synthetic questions for a single conversation"""
    try:
        result = await synthetic_question_generation_v1(client, conversation_id, conversation)
        return result
    except Exception as e:
        st.error(f"Error processing conversation {conversation_id}: {str(e)}")
        return SearchQueries(
            chain_of_thought=f"Error occurred: {str(e)}",
            queries=[]
        )

def display_conversation(conversation: Dict[str, Any], index: int):
    """Display a conversation with metadata"""
    cached = is_cached(conversation['conversation_hash'], conversation)
    cache_indicator = " ✅ (Cached)" if cached else " ⏳ (Not cached)"
    
    with st.expander(f"Conversation {index + 1}: {conversation['conversation_hash'][:8]}...{cache_indicator}"):
        
        # Metadata section
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Model:** {conversation['model']}")
            st.write(f"**Language:** {conversation['language']}")
        with col2:
            st.write(f"**Messages:** {conversation['conversation_length']}")
            st.write(f"**Country:** {conversation.get('country', 'Unknown')}")
        with col3:
            st.write(f"**Toxic:** {conversation['toxic']}")
            st.write(f"**Redacted:** {conversation['redacted']}")
            st.write(f"**Cached:** {'✅ Yes' if cached else '⏳ No'}")
        
        # Conversation content
        st.write("**Conversation:**")
        messages = conversation.get('conversation', [])
        for i, message in enumerate(messages[:10]):  # Show first 10 messages
            role = message.get('role', f'unknown_{i}')
            content = message.get('content', '')
            
            if role.lower() in ['user', 'human']:
                st.markdown(f"**👤 User:** {content}")
            elif role.lower() in ['assistant', 'ai']:
                st.markdown(f"**🤖 Assistant:** {content}")
            else:
                st.markdown(f"**{role}:** {content}")
        
        if len(messages) > 10:
            st.write(f"... and {len(messages) - 10} more messages")

def display_synthetic_questions(questions: SearchQueries, conversation_id: str):
    """Display generated synthetic questions"""
    st.write(f"**Generated Questions for {conversation_id[:8]}...:**")
    
    # Chain of thought
    with st.expander("Chain of Thought"):
        st.write(questions.chain_of_thought)
    
    # Questions
    if questions.queries:
        for i, query in enumerate(questions.queries, 1):
            st.write(f"{i}. {query}")
        
        # Quality evaluation
        st.write("**Quality Evaluation:**")
        col1, col2 = st.columns(2)
        with col1:
            quality_score = st.selectbox(
                "Overall Quality (1-5):",
                [1, 2, 3, 4, 5],
                index=2,
                key=f"quality_{conversation_id}"
            )
        with col2:
            diversity_score = st.selectbox(
                "Query Diversity (1-5):",
                [1, 2, 3, 4, 5],
                index=2,
                key=f"diversity_{conversation_id}"
            )
        
        feedback = st.text_area(
            "Additional Feedback:",
            placeholder="Any specific comments about the generated questions?",
            key=f"feedback_{conversation_id}"
        )
    else:
        st.warning("No questions were generated for this conversation.")

def main():
    st.title("🔍 Synthetic Question Generator")
    st.write("Generate and evaluate synthetic search queries from conversation data")
    
    # Load conversations
    if 'conversations' not in st.session_state:
        st.session_state.conversations = load_conversations(40)
    
    conversations = st.session_state.conversations
    st.success(f"Loaded {len(conversations)} conversations")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Controls")
        
        # Conversation selection
        selected_indices = st.multiselect(
            "Select conversations to process:",
            range(len(conversations)),
            default=list(range(min(5, len(conversations)))),  # Default to first 5
            format_func=lambda x: f"Conv {x+1}: {conversations[x]['conversation_hash'][:8]}..." + 
                        (" ✅" if is_cached(conversations[x]['conversation_hash'], conversations[x]) else "")
        )
        
        # Process button
        process_button = st.button("🚀 Process Selected Conversations", type="primary")
        
        # Cache management
        st.markdown("---")
        st.subheader("💾 Cache Management")
        
        cache_stats = get_cache_stats()
        if 'error' not in cache_stats:
            st.write(f"**Cached Items:** {cache_stats['count']}")
            st.write(f"**Cache Size:** {cache_stats['size']:,} bytes")
            
            # Show which selected conversations are cached
            if selected_indices:
                cached_count = sum(1 for idx in selected_indices 
                                 if is_cached(conversations[idx]['conversation_hash'], conversations[idx]))
                st.write(f"**Selected (Cached):** {cached_count}/{len(selected_indices)}")
        else:
            st.write("Cache status unavailable")
        
        # Clear cache button
        if st.button("🗑️ Clear Cache", help="Clear all cached results"):
            if clear_cache():
                st.success("Cache cleared!")
                st.rerun()
            else:
                st.error("Failed to clear cache")
        
        # OpenAI API key check
        st.markdown("---")
        if not os.getenv("OPENAI_API_KEY"):
            st.error("Please set OPENAI_API_KEY environment variable")
            st.stop()
        else:
            st.success("OpenAI API key configured")
    
    # Main content area
    tab1, tab2 = st.tabs(["📄 Conversations", "🎯 Generated Questions"])
    
    with tab1:
        st.header("Conversation Data")
        if selected_indices:
            for idx in selected_indices:
                display_conversation(conversations[idx], idx)
        else:
            st.info("Select conversations from the sidebar to view them here.")
    
    with tab2:
        st.header("Generated Synthetic Questions")
        
        if process_button and selected_indices:
            # Initialize results storage
            if 'results' not in st.session_state:
                st.session_state.results = {}
            
            # Get client
            client = get_openai_client()
            
            # Process conversations
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            async def process_all_conversations():
                results = {}
                for i, idx in enumerate(selected_indices):
                    conversation = conversations[idx]
                    conversation_id = conversation['conversation_hash']
                    
                    # Check if cached
                    cached = is_cached(conversation_id, conversation)
                    cache_status = " (cached)" if cached else " (generating...)"
                    
                    status_text.text(f"Processing conversation {i+1}/{len(selected_indices)}: {conversation_id[:8]}...{cache_status}")
                    
                    result = await process_conversation(client, conversation_id, conversation)
                    results[conversation_id] = result
                    
                    progress_bar.progress((i + 1) / len(selected_indices))
                
                return results
            
            # Run async processing
            try:
                results = asyncio.run(process_all_conversations())
                st.session_state.results.update(results)
                status_text.text("Processing complete!")
                st.success("All conversations processed successfully!")
            except Exception as e:
                st.error(f"Error during processing: {str(e)}")
        
        # Display results
        if 'results' in st.session_state and st.session_state.results:
            st.subheader("Results")
            
            for conversation_id, questions in st.session_state.results.items():
                with st.container():
                    st.markdown("---")
                    display_synthetic_questions(questions, conversation_id)
        
        elif not selected_indices:
            st.info("Select conversations from the sidebar and click 'Process' to generate questions.")
        
        else:
            st.info("Click 'Process Selected Conversations' to generate synthetic questions.")
    
    # Footer
    st.markdown("---")
    st.markdown("Built with Streamlit • Powered by OpenAI GPT-4o-mini")

if __name__ == "__main__":
    main() 