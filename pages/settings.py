import streamlit as st
from streamlit import session_state as state

def settings_page():
    st.write('Halo')
    del state.username
    st.write(list(state.keys()))
