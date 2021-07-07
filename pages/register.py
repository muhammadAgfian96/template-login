import streamlit as st
import hashlib, binascii, os
import time
import json
from easydict import EasyDict as edict


def div_register(state, roles=['grader', 'admin', 'superuser']):
    with st.form('register'):
        state.regis = edict()
        state.regis.name = st.text_input('Username')
        state.regis.pwd = st.text_input('Password', type='password')
        state.regis.repwd = st.text_input('Re-type Password', type='password', help='Don\'t input your bank password')
        state.regis.role = st.selectbox('Roles', roles)
        status_user = st.selectbox('Status', ['active', 'in-active'], 0)
        state.regis.status = True if status_user == 'active' else False
        state.regis.hash_pwd = hash_string(state.regis.pwd)
        submit_signup = st.form_submit_button('Sign-up')
    
    if submit_signup:
        isLoaded, data = load_user_file(state)
        if (state.regis.repwd != state.regis.pwd):
            state.status.regis= 'Not same password, check your password!'
            return False

        if state.regis.name == None or len(state.regis.name) < 4 \
            or state.regis.pwd == None or len(state.regis.pwd) < 4:
            state.status_regis= 'Your username or password is Null or too short (less than 4 character)!'
            return False

        isSaved = save_to_file(data, state)
        
        if not isLoaded:
            st.warning('Creating New DB')
        
        if isSaved:
            prog_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                prog_bar.progress(i)
            st.success('Succes Regis')
            time.sleep(1)
        else:
            st.warning('Ouch ch ch! username has been exist! Try Again!')
            time.sleep(1)

# ============= utils ==============
def hash_string(current_str):
    """Hash a current_str for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    str_hash = hashlib.pbkdf2_hmac('sha512', current_str.encode('utf-8'),
                                salt, 100000)
    str_hash = binascii.hexlify(str_hash)
    return (salt + str_hash).decode('ascii')

def remove_salt_from_hash(hash_string):
    return hash_string[64:]

def verify_string(saved_string, current_string):
    """Verify a stored password against one provided by user"""
    salt = saved_string[:64]
    saved_string = saved_string[64:]
    current_hash = hashlib.pbkdf2_hmac('sha512', 
                                  current_string.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    current_hash = binascii.hexlify(current_hash).decode('ascii')
    return current_hash == saved_string

def save_to_file(data, state, file='./userdb.json', action='w'):
    # this is for login this file
    with open(file, action) as f:
        # current_username = hash_string(state.regis.name)

        usernames = list(data['users'].keys())
        
        if state.regis.name not in usernames:
            data['users'][state.regis.name] =  {
                    'pwd': state.regis.hash_pwd,
                    'roles' : state.regis.role,
                    'status' : state.regis.status
            }
            json.dump(data, f, indent=2)
            isSaved = True
            state.regis = None
        else:
            json.dump(data, f, indent=2)
            isSaved = False
    return isSaved

def load_user_file(state, file='./userdb.json', action='w'):
    try:
        with open(file) as f:
            data = json.load(f)
            isLoaded = True
    except :
        data = {}
        data['users'] = {}
        isLoaded = False
    return isLoaded, data

def is_this_exist(usrname, file='./userdb.json', action='w'):
    user_data = {}
    with open(file, 'r') as f:
        data = json.load(f)
        usernames = list(data['users'].keys())
        if usrname in usernames:
            user_data = {
                'pwd_hash' : data['users'][usrname]['pwd'],
                'roles' : data['users'][usrname]['roles'],
                'status' : data['users'][usrname]['status'],
            }

    return user_data    
