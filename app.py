import streamlit as st

from streamlit import session_state as state
from state_management import *

from pages.login import login_page
from pages.home import home_page
from pages.settings import settings_page

def sidebar(pages):
    st.sidebar.write('## Navigation')
    sel_page = st.sidebar.radio('to', list(pages.keys()))
    return sel_page

def logout():
    state.login_status = False

def main():
    print('begin', list(state.keys()))
    print('begin', list(state.values()))
    default_value_state()

    if state.login_status == True:
        col = st.beta_columns((1,1,1,1,1,1))
        col[-1].button('Logout', on_click=logout)
        col[-1].write(f'Hi, **{state.username}**')


        pages = {
            'Home': home_page,
            'Settings': settings_page
        }

        # render page
        pages[sidebar(pages)]()
    else:
        login_page()
    

    return


if __name__ == "__main__":
    print('asd')
    # st.set_page_config(page_title='template login', page_icon='🦈', layout='wide', initial_sidebar_state='auto')
    main()