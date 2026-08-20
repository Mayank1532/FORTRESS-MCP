"""FORTRESS Security Control Center."""

import streamlit as st

st.set_page_config(
    page_title="FORTRESS-MCP",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ FORTRESS-MCP")
st.subheader("Zero-Trust Security Gateway")

st.info(
    "Phase 2 foundation is active. "
    "Security decisioning will be implemented in later phases."
)

st.metric("Gateway", "ONLINE")
st.metric("Security Policy", "FOUNDATION")
st.metric("MCP Gateway", "PENDING")
