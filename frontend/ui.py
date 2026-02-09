import os
import streamlit as st
import requests

API_URL = os.getenv("API_URL", "").strip()
if not API_URL:
    try:
        API_URL = st.secrets.get("API_URL", "").strip()
    except Exception:
        API_URL = ""
if not API_URL:
    API_URL = "http://localhost:8000"

api_label = API_URL.replace("https://", "").replace("http://", "")
st.markdown(
    f"<div style='color:#6b7280; font-size:0.9rem; margin-bottom:0.75rem;'>Connected API: {api_label}</div>",
    unsafe_allow_html=True,
)
st.set_page_config(page_title="Fiscal Sentinel", page_icon="FS", layout="wide")

LOGO_SVG = """
<svg width="44" height="44" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Fiscal Sentinel Logo">
  <defs>
    <linearGradient id="shield" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1F3B5B"/>
      <stop offset="100%" stop-color="#0B6AA2"/>
    </linearGradient>
  </defs>
  <path d="M32 4L54 10V30C54 45 44 57 32 60C20 57 10 45 10 30V10L32 4Z" fill="url(#shield)"/>
  <path d="M22 30L30 38L44 22" stroke="white" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""".strip()

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:0.25rem;">
      {LOGO_SVG}
      <div>
        <div style="font-size:2rem; font-weight:700; line-height:1.1;">Fiscal Sentinel</div>
        <div style="color:#6b7280; margin-top:4px;">Analyze transactions, spot issues, and draft dispute letters.</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def looks_like_letter(text: str) -> bool:
    t = text.lower()
    return any(
        k in t
        for k in ["dear ", "to whom it may concern", "subject:", "sincerely", "regards,"]
    )


def should_offer_letter(text: str) -> bool:
    t = text.lower()
    return ("draft" in t and "letter" in t) and (not looks_like_letter(text))


def _extract_error(res: requests.Response) -> str:
    try:
        detail = res.json().get("detail", "")
    except ValueError:
        detail = (res.text or "").strip()
    return f"Backend error ({res.status_code}). {detail}"


def _api_get(path: str):
    try:
        res = requests.get(f"{API_URL}{path}")
    except requests.RequestException as exc:
        return None, f"Backend request failed: {exc}"
    if not res.ok:
        return None, _extract_error(res)
    try:
        return res.json(), ""
    except ValueError:
        return None, "Backend returned non-JSON response."


def _api_post_json(path: str, payload: dict):
    try:
        res = requests.post(f"{API_URL}{path}", json=payload)
    except requests.RequestException as exc:
        return None, f"Backend request failed: {exc}"
    if not res.ok:
        return None, _extract_error(res)
    try:
        return res.json(), ""
    except ValueError:
        return None, "Backend returned non-JSON response."


def _api_post_file(path: str, uploaded_file):
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }
    try:
        res = requests.post(f"{API_URL}{path}", files=files)
    except requests.RequestException as exc:
        return None, f"Backend request failed: {exc}"
    if not res.ok:
        return None, _extract_error(res)
    try:
        return res.json(), ""
    except ValueError:
        return None, "Backend returned non-JSON response."


def send_message(user_text: str):
    history = st.session_state.msgs[:]
    with st.chat_message("user"):
        st.write(user_text)

    with st.spinner("Analyzing..."):
        payload, error = _api_post_json(
            "/analyze",
            {"query": user_text, "history": history, "debug": st.session_state.debug_mode},
        )
        if error:
            st.error(error)
            return
        reply = (payload or {}).get("response", "")
        if not reply:
            st.error("Backend response was missing the 'response' field.")
            return
        debug_payload = (payload or {}).get("debug") if st.session_state.debug_mode else None

    st.session_state.msgs.append({"role": "user", "content": user_text})
    if debug_payload:
        st.session_state.msgs.append({"role": "assistant", "content": reply, "debug": debug_payload})
    else:
        st.session_state.msgs.append({"role": "assistant", "content": reply})
    st.session_state.offer_letter = should_offer_letter(reply)

    with st.chat_message("assistant"):
        st.write(reply)
        if debug_payload:
            with st.expander("Routing debug"):
                st.json(debug_payload)


def _build_mapping_ui(columns: list[str], suggested: dict, schema: dict) -> dict:
    target_fields = schema.get("target_fields", [])
    mapping: dict[str, str] = {}
    options = [""] + columns
    for field in target_fields:
        name = field.get("name", "")
        if not name:
            continue
        label = f"{name}"
        if field.get("required"):
            label += " (required)"
        default = suggested.get(name, "")
        index = options.index(default) if default in options else 0
        selected = st.selectbox(label, options, index=index, key=f"map_{name}")
        if selected:
            mapping[name] = selected
    return mapping


if "msgs" not in st.session_state:
    st.session_state.msgs = []
if "offer_letter" not in st.session_state:
    st.session_state.offer_letter = False
if "tx" not in st.session_state:
    st.session_state.tx = []
if "preview" not in st.session_state:
    st.session_state.preview = None
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False
if "vector_db_status" not in st.session_state:
    st.session_state.vector_db_status = None

tab_tx, tab_chat = st.tabs(["Transactions", "Assistant"])

with tab_tx:
    col_left, col_right = st.columns([1.1, 1.4])

    with col_left:
        st.subheader("Upload & Preview")
        uploaded = st.file_uploader("Upload CSV, JSON, or PDF", type=["csv", "json", "pdf"])

        action_cols = st.columns(2)
        with action_cols[0]:
            if uploaded and st.button("Preview & Map"):
                preview_payload, error = _api_post_file("/transactions/preview", uploaded)
                if error:
                    st.error(error)
                else:
                    st.session_state.preview = preview_payload
                    st.success("Preview generated. Map the columns below and confirm.")

        with action_cols[1]:
            if uploaded and st.button("Upload Directly"):
                upload_payload, error = _api_post_file("/transactions/upload", uploaded)
                if error:
                    st.error(error)
                else:
                    count = upload_payload.get("count", 0)
                    st.success(f"Uploaded {count} transactions.")
                    tx_payload, error = _api_get("/transactions")
                    if error:
                        st.error(error)
                    else:
                        st.session_state.tx = tx_payload or []

        preview = st.session_state.preview
        if preview:
            st.divider()
            st.subheader("Preview Summary")
            st.write(f"Source: {preview.get('source', 'unknown')}")
            stats = preview.get("confidence_stats", {})
            if stats:
                st.write(
                    f"Confidence avg: {stats.get('avg', 0.0)} | min: {stats.get('min', 0.0)} "
                    f"| max: {stats.get('max', 0.0)} | rows: {stats.get('count', 0)}"
                )

            sample_rows = preview.get("sample_rows", [])
            if sample_rows:
                st.dataframe(sample_rows, use_container_width=True, height=240)

            st.subheader("Confirm Column Mapping")
            columns = preview.get("columns", [])
            suggested = preview.get("suggested_mapping", {})
            schema = preview.get("schema", {})
            mapping = _build_mapping_ui(columns, suggested, schema)

            confirm_cols = st.columns(2)
            with confirm_cols[0]:
                if st.button("Confirm & Import"):
                    preview_id = preview.get("preview_id")
                    if not preview_id:
                        st.error("Missing preview_id from server.")
                    else:
                        confirm_payload, error = _api_post_json(
                            "/transactions/confirm",
                            {"preview_id": preview_id, "mapping": mapping},
                        )
                        if error:
                            st.error(error)
                        else:
                            count = confirm_payload.get("count", 0)
                            st.success(f"Imported {count} transactions.")
                            st.session_state.preview = None
                            tx_payload, error = _api_get("/transactions")
                            if error:
                                st.error(error)
                            else:
                                st.session_state.tx = tx_payload or []

            with confirm_cols[1]:
                if st.button("Clear Preview"):
                    st.session_state.preview = None

    with col_right:
        st.subheader("Current Transactions")
        st.caption("Loaded transactions are used for analysis and letter drafting.")

        status_cols = st.columns(2)
        with status_cols[0]:
            if st.button("Check Vector DB"):
                status_payload, error = _api_get("/vector-db/health")
                if error:
                    st.error(error)
                    st.session_state.vector_db_status = None
                else:
                    st.session_state.vector_db_status = status_payload

        with status_cols[1]:
            status = st.session_state.vector_db_status
            if status:
                provider = status.get("provider", "unknown")
                collection = status.get("collection", "unknown")
                vectors = status.get("vectors_count", 0)
                st.write(f"Provider: {provider}")
                st.write(f"Collection: {collection}")
                st.write(f"Vectors: {vectors}")

        load_cols = st.columns(2)
        with load_cols[0]:
            if st.button("Load Current"):
                tx_payload, error = _api_get("/transactions")
                if error:
                    st.error(error)
                else:
                    st.session_state.tx = tx_payload or []

        with load_cols[1]:
            if st.button("Connect Bank (Mock)"):
                tx_payload, error = _api_get("/transactions")
                if error:
                    st.error(error)
                else:
                    st.session_state.tx = tx_payload or []

        tx = st.session_state.tx or []
        if tx:
            st.write(f"Transactions loaded: {len(tx)}")
            st.dataframe(tx[:25], use_container_width=True, height=420)
        else:
            st.info("No transactions loaded yet. Upload a file or connect the mock bank feed.")

with tab_chat:
    st.subheader("Ask Fiscal Sentinel")
    st.caption('Example: "What is the highest transaction in my account?"')
    st.checkbox("Show routing debug", key="debug_mode")

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.write(m["content"])
            if m.get("debug"):
                with st.expander("Routing debug"):
                    st.json(m["debug"])

    if prompt := st.chat_input("Ask about your transactions..."):
        st.session_state.offer_letter = False
        send_message(prompt)

    if st.session_state.offer_letter:
        if st.button("Draft the letter"):
            st.session_state.offer_letter = False
            send_message("Yes, please draft the letter.")
