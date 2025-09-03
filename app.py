"""
California Procurement Assistant - Streamlit Interface
"""
import streamlit as st
from pymongo import MongoClient
from config import MONGODB_CONFIG
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agent
try:
    from ollama_agent import OllamaAgent as GPTAgent
    agent_type = "Ollama"
    agent_available = True
except ImportError:
    agent_available = False
    st.error("No agent found! Please check ollama_agent.py")

# Page configuration
st.set_page_config(
    page_title="California Procurement Assistant",
    page_icon="🏛️",
    layout="wide"
)

# Initialize session state
if 'agent' not in st.session_state and agent_available:
    try:
        st.session_state.agent = GPTAgent()
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        st.stop()
    
if 'messages' not in st.session_state:
    st.session_state.messages = []

def get_stats():
    """Get database statistics"""
    try:
        client = MongoClient(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'])
        db = client[MONGODB_CONFIG['database']]
        collection = db[MONGODB_CONFIG['collection']]
        
        stats = {
            'records': collection.count_documents({}),
            'departments': len(collection.distinct('Department Name')),
            'suppliers': len(collection.distinct('Supplier Name'))
        }
        
        pipeline = [{'$group': {'_id': None, 'total': {'$sum': '$Total Price'}}}]
        result = list(collection.aggregate(pipeline))
        if result:
            stats['spending'] = result[0]['total']
        
        client.close()
        return stats
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Main title
st.title("🏛️ California Procurement AI Assistant")
st.markdown(f"Ask questions about procurement data (Using {agent_type})")

# Sidebar
with st.sidebar:
    st.header("📊 Database Stats")
    
    stats = get_stats()
    if stats:
        st.metric("Records", f"{stats['records']:,}")
        st.metric("Departments", stats['departments'])
        st.metric("Suppliers", f"{stats['suppliers']:,}")
        if 'spending' in stats:
            st.metric("Total Spending", f"${stats['spending']/1e9:.1f}B")
    else:
        st.warning("Could not load database stats")
    
    st.divider()
    
    st.header("💡 Example Questions")
    
    examples = [
        "What is the total spending in 2014?",
        "Which department spent the most?",
        "Top 5 suppliers by revenue",
        "Average purchase amount",
        "How many purchases in 2015?",
        "Most frequently ordered items",
        "Show purchases over $1 million"
    ]
    
    for ex in examples:
        if st.button(ex, key=ex):
            st.session_state.messages.append({"role": "user", "content": ex})
            with st.spinner("Processing..."):
                response = st.session_state.agent.answer_question(ex)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    st.divider()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat area
st.header("💬 Chat")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask about procurement data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            start_time = time.time()
            try:
                response = st.session_state.agent.answer_question(prompt)
                elapsed = time.time() - start_time
                
                st.markdown(response)
                st.caption(f"Response time: {elapsed:.1f}s")
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"Error: {e}"
                st.error(error_msg)
                st.info("Try rephrasing your question or use a simpler query.")

# About section
with st.expander("ℹ️ About"):
    st.markdown(f"""
    **Data Source:** California State Procurement (2012-2015)
    
    **Total Records:** 346,018 purchases
    
    **AI Model:** {agent_type}
    
    **Features:**
    - Natural language queries
    - MongoDB aggregation
    - Real-time analysis
    
    **Sample Questions:**
    - Total spending by year
    - Department/supplier analysis
    - Most frequently ordered items
    - Purchase statistics
    """)

st.divider()
st.caption("Built with Streamlit, MongoDB, and AI")