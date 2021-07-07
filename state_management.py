import streamlit as st



def default_value_state(state):

    if state.login_status is None:
        state.login_status = False


    if state.sel_page is None:
        state.sel_page = 'Home'


    