import streamlit as st
from streamlit import session_state as state

def home_page():


    st.write(list(state.keys()))
    st.write(list(state.values()))