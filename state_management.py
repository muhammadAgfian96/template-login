from streamlit import session_state as state



def default_value_state():
    print('before', list(state.keys()))
    print('before', list(state.values()))
    if 'login_status' not in state:
        state.login_status = False

    # if 'username' not in state:
    #     state.username = ''

    # if 'pwd' not in state:
    #     state.pwd = ''


    if 'sel_page' not in state:
        state.sel_page = 'Home'

    print('after', list(state.keys()))
    print('after', list(state.values()))
    print('ini jalan')

    