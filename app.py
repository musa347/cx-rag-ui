import streamlit as st
import requests
import json
import time

st.set_page_config(
    page_title="IRIS AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: #f0f0f0;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
    }
    .query-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .answer-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .confidence-high {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
    }
    .confidence-medium {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
    }
    .citation-card {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(15px);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid rgba(255,255,255,0.3);
        font-size: 0.9rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

# Professional header
st.markdown("""
<div class="main-header">
    <h1>IRIS AI</h1>
    <p>Advanced Customer Intelligence System</p>
</div>
""", unsafe_allow_html=True)

# Configuration
API_URL = st.secrets.get("API_URL", "https://cx-rag-backend.onrender.com")

# Main interface with columns
col1, col2 = st.columns([2, 1])

with col1:
    # System description
    st.info("💡 **What is IRIS AI?** - An intelligent customer experience assistant powered by RAG technology. It analyzes company policies and historical complaint data to provide instant, accurate guidance for customer service scenarios.")
    
    st.markdown('<div class="query-box">', unsafe_allow_html=True)
    st.markdown("### Ask IRIS")

    # Query input
    query = st.text_area(
        "",
        placeholder="How should I handle a customer complaint about online banking access?",
        height=100,
        label_visibility="collapsed"
    )

    # Endpoint and query type selection
    col_endpoint, col_type = st.columns([1, 1])
    with col_endpoint:
        endpoint_type = st.selectbox(
            "Query Mode:",
            ["General Query", "Policy Guidance", "Complaint Analysis"]
        )
    with col_type:
        if endpoint_type == "General Query":
            query_type = st.selectbox("Data Type:", ["both", "policy", "complaint"])
        else:
            st.write("")  # spacing

    # Ask button
    ask_button = st.button("Ask IRIS", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Response area
    if ask_button and query:
        with st.spinner("Processing..."):
            try:
                # Map endpoint types to URLs and payloads
                if endpoint_type == "Policy Guidance":
                    endpoint = "/api/cx/policy-guidance"
                    payload = {"scenario": query}
                elif endpoint_type == "Complaint Analysis":
                    endpoint = "/api/cx/complaint-analysis"
                    payload = {"complaint": query}
                else:  # General Query
                    endpoint = "/api/cx/answer"
                    payload = {"query": query, "type": query_type}

                response = requests.post(
                    f"{API_URL}{endpoint}",
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()

                    # Add to history
                    st.session_state.history.append({
                        "query": query,
                        "endpoint": endpoint_type,
                        "type": query_type if endpoint_type == "General Query" else endpoint_type,
                        "answer": result.get("answer", "No answer"),
                        "confidence": result.get("confidence", "UNKNOWN"),
                        "timestamp": time.strftime("%H:%M")
                    })

                    # Answer display
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown("### Response")
                    st.write(result.get("answer", "No answer"))

                    # Confidence display
                    confidence = result.get("confidence", "UNKNOWN")
                    if confidence == "HIGH":
                        st.markdown(f'<div class="confidence-high">HIGH CONFIDENCE</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="confidence-medium">{confidence} CONFIDENCE</div>', unsafe_allow_html=True)

                    # Next action
                    next_action = result.get("nextAction")
                    if next_action:
                        st.markdown("### Recommended Action")
                        st.info(next_action)

                    # Risk flags (if any)
                    risks = result.get("risks", [])
                    if risks:
                        st.markdown("### Risk Alerts")
                        for risk in risks:
                            st.warning(f"**{risk.get('type')}**: {risk.get('description')}")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # Citations
                    citations = result.get("citations", [])
                    if citations:
                        st.markdown("### Knowledge Sources")
                        for citation in citations:
                            st.markdown(f"""
                            <div class="citation-card">
                                <strong>{citation.get('policyName', 'Unknown Policy')}</strong><br>
                                <em>{citation.get('sectionTitle', 'Unknown Section')}</em>
                            </div>
                            """, unsafe_allow_html=True)

                else:
                    st.error(f"Error: {response.text}")

            except Exception as e:
                st.error(f"Connection error: {str(e)}")

# Sidebar
with col2:
    st.markdown("### Control Panel")

    # Status check
    if st.button("System Status", use_container_width=True):
        try:
            response = requests.get(f"{API_URL}/api/health", timeout=10)
            if response.status_code == 200:
                st.success("System Online")
            else:
                st.error("System Offline")
        except:
            st.error("Connection Failed")

    # Query History
    if st.session_state.history:
        st.markdown("### Recent Queries")
        if st.button("Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()

        for i, item in enumerate(reversed(st.session_state.history[-5:])):
            with st.expander(f"{item['timestamp']} - {item['query'][:25]}..."):
                endpoint = item.get('endpoint', 'General Query')
                st.write(f"**Mode:** {endpoint}")
                if endpoint == "General Query":
                    st.write(f"**Type:** {item.get('type', 'both')}")
                st.write(f"**Answer:** {item['answer'][:100]}...")
                st.write(f"**Confidence:** {item['confidence']}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Powered by Advanced RAG Technology</div>",
    unsafe_allow_html=True
)
