import streamlit as st
import requests

API_URL = "http://localhost:8000"
st.set_page_config(page_title="Fiscal Sentinel", page_icon="🛡️", layout="wide")
st.title("🛡️ Fiscal Sentinel")

# Sidebar: Transactions
with st.sidebar:
    st.header("Bank Feed (Mock)")
    if st.button("Connect Bank"):
        res = requests.get(f"{API_URL}/transactions")
        st.session_state['tx'] = res.json()
    
    if 'tx' in st.session_state:
        for t in st.session_state['tx']:
            st.warning(f"{t['merchant_name']} - ${t['amount']}")

# Main: Chat
if "msgs" not in st.session_state: st.session_state.msgs = []

for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.write(m["content"])

if prompt := st.chat_input("Scan for threats..."):
    history = st.session_state.msgs[:]
    with st.chat_message("user"): st.write(prompt)
    
    with st.spinner("Analyzing..."):
        res = requests.post(
            f"{API_URL}/analyze",
            json={"query": prompt, "history": history},
        )
        reply = res.json()["response"]
        st.session_state.msgs.append({"role": "user", "content": prompt})
        st.session_state.msgs.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"): st.write(reply)
