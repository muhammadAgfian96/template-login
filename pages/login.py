import streamlit as st
import hashlib, binascii, os
import time
import json
from easydict import EasyDict as edict
from pages.register import is_this_exist, verify_string

def submit_login(state):
    bar_progrress = st.progress(0)
    data = is_this_exist(state.username)
    if len(data) <=0:
        st.error('Incorrect Username/Password')
        time.sleep(1)
        return
    password_provided = data.get("pwd_hash")
    isMatchPass = verify_string(password_provided,  state.pwd)
    if not isMatchPass:
        st.error('Incorrect Username/Password')
        time.sleep(1)
    else:
        state.user = edict()
        state.user.name = state.username
        state.user.role = data.get('roles')
        state.user.status = data.get('status')
        state.login_status = isMatchPass

def login_page(state):
    st.write('# Welcome Annotation App')

    with st.form('login'):
        st.write('### Login')
        state.username = st.text_input('Username')
        state.pwd = st.text_input('Password', type='password')
        submit = st.form_submit_button('Sign In')

    if submit:
        submit_login(state)