import streamlit as st
from streamlit import session_state as state
import hashlib, binascii, os
import time

def submit_login():
    bar_progrress = st.progress(0)
    with st.spinner('Wait we check you...'):
        for i in range(0,101):
            bar_progrress.progress(i)
            time.sleep(0.005)
    
    if state.username != '' and state.pwd != '':
        state.login_status = True
        st.success('Succes Login!')
        st.balloons()
    else:
        st.error('Failed Login!')

def login_page():
    st.write('# Welcome Multispectral App')
    with st.form('login'):
        state.username = st.text_input('Username')
        state.pwd = st.text_input('Password', type='password')
        st.form_submit_button('Sign In', on_click=submit_login)
    st.write('Halo')
    # if submit:
    #     try:
    #         data = get_user_by_name(name)
    #         password_provided = data.get("pwd")
    #         isMatchPass = verify_password(password_provided, pwd)
    #         if not isMatchPass:
    #             st.error('Incorrect Username/Password')
    #             time.sleep(1)
    #         else:
    #             state.user = edict()
    #             state.user.name = name
    #             state.user.role = data.get('role')
    #             state.user.status = data.get('status')
    #         return isMatchPass
    #         # return state.login_status if state.login_status else False

    #     except TypeError:
    #         st.error('Incorrect Username/Password')

# ============================= utils ============================
def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')