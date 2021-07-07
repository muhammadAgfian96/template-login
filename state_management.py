from streamlit import session_state as state



def default_value_state():
    if 'login_status' not in state:
        state.login_status = False

    if 'username' not in state:
        state.username = ''

    if 'pwd' not in state:
        state.pwd = ''


    if 'sel_page' not in state:
        state.sel_page = 'home'

    