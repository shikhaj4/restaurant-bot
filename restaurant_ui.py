# restaurant_ui.py
import streamlit as st
import requests

st.set_page_config(page_title="Restaurant Chatbot")
st.title("Restaurant Chatbot")

query = st.text_input("Ask about restaurants:")

if query:
    with st.spinner("Finding restaurants..."):
        try:
            resp = requests.post("http://127.0.0.1:8000/chat", json={"query": query}).json()
            parsed = resp["parsed"]

            st.subheader("Recommended Restaurants:")
            for r in parsed["restaurants"]:
                st.write(f"- {r}")

            st.subheader("Explanation:")
            st.write(parsed["explanation"])
        except Exception as e:
            st.error(f"Error: {e}")
