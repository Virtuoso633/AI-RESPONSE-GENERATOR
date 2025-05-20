# Add content to frontend/app.py
import streamlit as st
import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# API endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

st.set_page_config(
    page_title="AI Response Generator",
    page_icon="🤖",
    layout="wide"
)

st.title("AI Response Generator")

# Sidebar for user ID and history
with st.sidebar:
    st.header("User Settings")
    user_id = st.text_input("Enter User ID", value="user123")
    
    st.header("History")
    if st.button("Refresh History"):
        try:
            response = requests.get(f"{API_URL}/history?user_id={user_id}")
            if response.status_code == 200:
                st.session_state.history = response.json()
            else:
                st.error(f"Error fetching history: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Display history if available
    if "history" in st.session_state:
        for item in st.session_state.history:
            with st.expander(f"{item['query'][:30]}... ({item['created_at'][:10]})"):
                st.write("**Query:**")
                st.write(item["query"])
                st.write("**Casual Response:**")
                st.write(item["casual_response"])
                st.write("**Formal Response:**")
                st.write(item["formal_response"])

# Main area for query input and responses
st.header("Ask a Question")

with st.form("query_form"):
    query = st.text_area("Enter your query", height=100)
    submitted = st.form_submit_button("Generate Responses")
    
    if submitted and query:
        with st.spinner("Generating responses..."):
            try:
                payload = {
                    "user_id": user_id,
                    "query": query
                }
                
                response = requests.post(f"{API_URL}/generate", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Store in session state for display
                    st.session_state.casual_response = result["casual_response"]
                    st.session_state.formal_response = result["formal_response"]
                    
                    # Refresh history
                    history_response = requests.get(f"{API_URL}/history?user_id={user_id}")
                    if history_response.status_code == 200:
                        st.session_state.history = history_response.json()
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Display responses if available
if "casual_response" in st.session_state and "formal_response" in st.session_state:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Casual Response")
        st.write(st.session_state.casual_response)
    
    with col2:
        st.subheader("Formal Response")
        st.write(st.session_state.formal_response)
