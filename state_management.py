import streamlit as st
# from streamlit import session_state as state



def default_value_state(state):
    # print('before', list(state.keys()))
    # print('before', list(state.values()))
    if state.login_status is None:
        state.login_status = False

    # if 'username' not in state:
    #     state.username = ''

    # if 'pwd' not in state:
    #     state.pwd = ''


    if state.sel_page is None:
        state.sel_page = 'Home'

    # print('after', list(state.keys()))
    # print('after', list(state.values()))
    # print('ini jalan')

    