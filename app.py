import streamlit as st
import requests
import json

st.set_page_config(page_title="CX RAG System", page_icon="🤖")

# Configuration
API_URL = st.secrets.get("API_URL", "https://cx-rag-backend.onrender.com")

st.title("🤖 CX RAG System")
st.markdown("**Free Customer Intelligence System**")

# Simple interface
query = st.text_area("Ask a question:", placeholder="How should I handle a customer complaint?")
query_type = st.selectbox("Type:", ["both", "policy", "complaint"])

if st.button("Get Answer", type="primary"):
    if query:
        with st.spinner("Processing..."):
            try:
                response = requests.post(
                    f"{API_URL}/api/cx/answer",
                    json={"query": query, "type": query_type},
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()

                    st.success("**Answer:**")
                    st.write(result.get("answer", "No answer"))

                    confidence = result.get("confidence", "UNKNOWN")
                    if confidence == "HIGH":
                        st.success(f"🟢 Confidence: {confidence}")
                    else:
                        st.warning(f"🟡 Confidence: {confidence}")

                    citations = result.get("citations", [])
                    if citations:
                        st.subheader("📚 Sources")
                        for citation in citations:
                            st.info(f"**{citation.get('policyName')}** - {citation.get('sectionTitle')}")

                else:
                    st.error(f"Error: {response.text}")

            except Exception as e:
                st.error(f"Connection error: {str(e)}")

# Health check
if st.sidebar.button("Check Status"):
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=10)
        if response.status_code == 200:
            st.sidebar.success("✅ System Online")
        else:
            st.sidebar.error("❌ System Offline")
    except:
        st.sidebar.error("❌ Connection Failed")
