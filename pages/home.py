import streamlit as st
from streamlit import session_state as state

def logout():
    state.login_status = False

def home_page():

    st.write(list(state.keys()))
    st.write('Hi,', state.username)
    st.button('Logout', on_click=logout)