#!/usr/bin/env python3
"""
Streamlit app for searching and visualizing conversations
"""

import asyncio
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
import sqlite3

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import DAOs
from utils.dao.wildchat_dao_chromadb import WildChatDAOChromaDB
from utils.dao.wildchat_dao_turbopuffer import WildChatDAOTurbopuffer
from utils.dao.wildchat_dao import SearchRequest, SearchType

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Conversation Search",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "selected_conversation" not in st.session_state:
    st.session_state.selected_conversation = None


def parse_conversation(conversation_string: str) -> list:
    """Parse conversation string into list of messages"""
    messages = []
    
    # Check if it's XML format
    if '<message role=' in conversation_string:
        # XML parsing - look for message tags
        import re
        pattern = r'<message role="(user|assistant)">(.*?)</message>'
        matches = re.findall(pattern, conversation_string, re.DOTALL)
        
        for role, content in matches:
            messages.append({
                "role": role,
                "content": content.strip()
            })
    else:
        # Plain text format with "User:" and "A:" prefixes
        lines = conversation_string.split('\n\n')
        current_role = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("User:"):
                # Save previous message if exists
                if current_role and current_content:
                    messages.append({
                        "role": current_role,
                        "content": '\n'.join(current_content).strip()
                    })
                current_role = "user"
                current_content = [line[5:].strip()]  # Remove "User:" prefix
            elif line.startswith("A:"):
                # Save previous message if exists
                if current_role and current_content:
                    messages.append({
                        "role": current_role,
                        "content": '\n'.join(current_content).strip()
                    })
                current_role = "assistant"
                current_content = [line[2:].strip()]  # Remove "A:" prefix
            else:
                # Continuation of previous message
                if current_content:
                    current_content.append(line)
        
        # Don't forget the last message
        if current_role and current_content:
            messages.append({
                "role": current_role,
                "content": '\n'.join(current_content).strip()
            })
    
    return messages


def get_synthetic_queries(conversation_hash: str) -> list:
    """Get synthetic queries generated for a conversation"""
    db_path = Path(__file__).parent / "data" / "synthetic_queries.db"
    
    if not db_path.exists():
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT prompt_version, query 
        FROM synthetic_queries 
        WHERE conversation_hash = ?
        ORDER BY prompt_version
    """, (conversation_hash,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results


async def perform_search(query: str, backend: str, search_type: str, top_k: int):
    """Execute search using selected backend"""
    # Create DAO based on backend selection
    if backend == "ChromaDB":
        dao = WildChatDAOChromaDB()
    else:  # Turbopuffer
        dao = WildChatDAOTurbopuffer()
    
    try:
        # Connect to database
        await dao.connect()
        
        # Create search request
        search_type_enum = SearchType[search_type]
        request = SearchRequest(
            query=query,
            top_k=top_k,
            search_type=search_type_enum
        )
        
        # Perform search
        results = await dao.search(request)
        
        # Disconnect
        await dao.disconnect()
        
        return results
        
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return None


def main():
    st.title("🔍 Conversation Search")
    st.markdown("Search for similar conversations using vector similarity or full-text search")
    
    # Sidebar for search controls
    with st.sidebar:
        st.header("Search Settings")
        
        # Backend selection
        backend = st.selectbox(
            "Select Backend",
            ["Turbopuffer", "ChromaDB"],
            help="Choose the database backend for search"
        )
        
        # Search type selection
        if backend == "ChromaDB":
            search_types = ["VECTOR"]
        else:
            search_types = ["VECTOR", "FULL_TEXT", "HYBRID"]
        
        search_type = st.selectbox(
            "Search Type",
            search_types,
            help="Vector: Semantic similarity | Full-text: Keyword matching | Hybrid: Both"
        )
        
        # Number of results
        top_k = st.slider(
            "Number of Results",
            min_value=1,
            max_value=20,
            value=5,
            help="Number of similar conversations to retrieve"
        )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Search")
        
        # Search input
        query = st.text_input(
            "Enter your search query",
            placeholder="e.g., How do I learn Python programming?",
            help="Enter a question or topic to find similar conversations"
        )
        
        # Search button
        if st.button("🔍 Search", type="primary", disabled=not query):
            with st.spinner(f"Searching with {backend}..."):
                # Run async search
                results = asyncio.run(perform_search(query, backend, search_type, top_k))
                
                if results:
                    st.session_state.search_results = results
                    st.success(f"Found {len(results.results)} results in {results.query_time_ms:.2f}ms")
        
        # Display search results
        if st.session_state.search_results:
            st.subheader("Search Results")
            
            for i, result in enumerate(st.session_state.search_results.results):
                # Check if this conversation has synthetic queries
                conv_hash = result.metadata.get('hash', '')
                has_synthetic = bool(get_synthetic_queries(conv_hash)) if conv_hash else False
                
                title = f"Result {i+1} (Score: {result.score:.4f})"
                if has_synthetic:
                    title += " 🔍"
                
                with st.expander(title):
                    # Show metadata
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.caption(f"**Language:** {result.metadata.get('language', 'N/A')}")
                        st.caption(f"**Model:** {result.metadata.get('model_name', 'N/A')}")
                    with col_b:
                        st.caption(f"**Timestamp:** {result.metadata.get('timestamp', 'N/A')}")
                        st.caption(f"**Turns:** {result.metadata.get('conversation_length', 'N/A')}")
                    
                    if has_synthetic:
                        st.caption("🔍 **Has synthetic queries**")
                    
                    # Show preview
                    st.text(result.text[:200] + "..." if len(result.text) > 200 else result.text)
                    
                    # Button to view full conversation
                    if st.button(f"View Full Conversation", key=f"view_{i}"):
                        st.session_state.selected_conversation = result
    
    with col2:
        st.subheader("Conversation Viewer")
        
        if st.session_state.selected_conversation:
            result = st.session_state.selected_conversation
            
            # Display metadata
            st.markdown(f"**Score:** {result.score:.4f} | **Language:** {result.metadata.get('language', 'N/A')} | **Model:** {result.metadata.get('model_name', 'N/A')}")
            
            # Check for synthetic queries
            conversation_hash = result.metadata.get('hash', '')
            synthetic_queries = get_synthetic_queries(conversation_hash) if conversation_hash else []
            
            if synthetic_queries:
                with st.expander(f"🔍 Synthetic Queries Generated ({len(synthetic_queries)})"):
                    for version, query in synthetic_queries:
                        st.markdown(f"**{version}:** {query}")
            
            st.divider()
            
            # Parse and display conversation
            st.markdown("**Full Conversation:**")
            messages = parse_conversation(result.conversation_string)
            
            for msg in messages:
                if msg["role"] == "user":
                    st.chat_message("user").write(msg["content"])
                else:
                    st.chat_message("assistant").write(msg["content"])
        else:
            st.info("Select a conversation from the search results to view it here")


if __name__ == "__main__":
    main()