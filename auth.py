
import streamlit as st

def login():
    st.sidebar.header("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username == "admin" and password == "pass123":
            st.session_state["auth"] = True
            st.experimental_rerun()
        else:
            st.sidebar.error("Invalid credentials")

def is_logged_in():
    return st.session_state.get("auth", False)
