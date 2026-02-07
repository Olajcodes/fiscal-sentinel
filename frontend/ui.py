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
        try:
            res = requests.post(
                f"{API_URL}/analyze",
                json={"query": user_text, "history": history},
            )
        except requests.RequestException as exc:
            st.error(f"Backend request failed: {exc}")
            return

        if not res.ok:
            detail = ""
            try:
                detail = res.json().get("detail", "")
            except ValueError:
                detail = (res.text or "").strip()
            st.error(f"Backend error ({res.status_code}). {detail}")
            return

        try:
            payload = res.json()
        except ValueError:
            st.error(f"Backend returned non-JSON response (status {res.status_code}).")
            return
        reply = payload.get("response", "")
        if not reply:
            st.error("Backend response was missing the 'response' field.")
            return

    st.session_state.msgs.append({"role": "user", "content": user_text})
    st.session_state.msgs.append({"role": "assistant", "content": reply})
    st.session_state.offer_letter = should_offer_letter(reply)

    with st.chat_message("assistant"):
        st.write(reply)

# Sidebar: Transactions
with st.sidebar:
    st.header("Bank Feed (Mock)")
    uploaded = st.file_uploader("Upload bank CSV, JSON, or PDF", type=["csv", "json", "pdf"])
    if uploaded and st.button("Upload Transactions"):
        files = {
            "file": (
                uploaded.name,
                uploaded.getvalue(),
                uploaded.type or "application/octet-stream",
            )
        }
        res = requests.post(f"{API_URL}/transactions/upload", files=files)
        if res.ok:
            st.success(f"Uploaded {res.json().get('count', 0)} transactions.")
            st.session_state["tx"] = requests.get(f"{API_URL}/transactions").json()
        else:
            st.error(res.json().get("detail", "Upload failed."))

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
