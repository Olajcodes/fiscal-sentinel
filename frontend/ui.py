import streamlit as st
import requests

API_URL = "http://localhost:8000"
st.set_page_config(page_title="Fiscal Sentinel", page_icon="🛡️", layout="wide")
st.title("🛡️ Fiscal Sentinel")

def looks_like_letter(text: str) -> bool:
    t = text.lower()
    return any(
        k in t
        for k in ["dear ", "to whom it may concern", "subject:", "sincerely", "regards,"]
    )


def should_offer_letter(text: str) -> bool:
    t = text.lower()
    return ("draft" in t and "letter" in t) and (not looks_like_letter(text))


def send_message(user_text: str):
    history = st.session_state.msgs[:]
    with st.chat_message("user"):
        st.write(user_text)

    with st.spinner("Analyzing..."):
        res = requests.post(
            f"{API_URL}/analyze",
            json={"query": user_text, "history": history},
        )
        reply = res.json()["response"]

    st.session_state.msgs.append({"role": "user", "content": user_text})
    st.session_state.msgs.append({"role": "assistant", "content": reply})
    st.session_state.offer_letter = should_offer_letter(reply)

    with st.chat_message("assistant"):
        st.write(reply)

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
if "offer_letter" not in st.session_state: st.session_state.offer_letter = False

for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.write(m["content"])

if prompt := st.chat_input("Scan for threats..."):
    st.session_state.offer_letter = False
    send_message(prompt)

if st.session_state.offer_letter:
    if st.button("Draft the letter"):
        st.session_state.offer_letter = False
        send_message("Yes, please draft the letter.")
