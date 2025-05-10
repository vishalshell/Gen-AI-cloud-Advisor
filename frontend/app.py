import os
import requests
import streamlit as st

API_URL = os.getenv('API_URL', 'http://localhost:8000')

st.set_page_config(page_title="Gen‑AI Cloud Advisor (AWS)")
st.title("💸 Gen‑AI Cloud Advisor (AWS)")

tab1, tab2 = st.tabs(["Chat", "Rightsizing"])

with tab1:
    v_prompt = st.text_area("Ask about your AWS bill:", height=150)
    if st.button("Ask", key="btn_chat"):
        if not v_prompt.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Contacting FinOps AI…"):
                v_resp = requests.post(f"{API_URL}/chat", json={"prompt": v_prompt})
            if v_resp.status_code == 200:
                st.success(v_resp.json()["answer"])
            else:
                st.error(f"Error {v_resp.status_code}: {v_resp.text}")

with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        instance_id = st.text_input("Instance ID", key="instance_id")
    with col2:
        avg_cpu = st.number_input("Avg CPU %", min_value=0.0, max_value=100.0, value=30.0)
    with col3:
        avg_mem = st.number_input("Avg Memory %", min_value=0.0, max_value=100.0, value=40.0)

    if st.button("Get suggestion", key="btn_rightsize"):
        if not instance_id.strip():
            st.warning("Please enter an instance id.")
        else:
            with st.spinner("Consulting AI duo…"):
                v_resp = requests.post(f"{API_URL}/rightsizing",
                                       json={"instance_id": instance_id,
                                             "avg_cpu": avg_cpu,
                                             "avg_mem": avg_mem})
            if v_resp.status_code == 200:
                data = v_resp.json()
                st.subheader(f"Decision: {data['decision']}")
                st.write(data['reasoning'])
                with st.expander("Model opinions"):
                    st.write("**GPT‑4o**:", data["gpt_opinion"])
                    st.write("**Gemini**:", data["gemini_opinion"])
            else:
                st.error(f"Error {v_resp.status_code}: {v_resp.text}")
