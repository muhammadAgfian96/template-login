import os
import random

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

def main():
    st.set_page_config(page_title='template login',
                page_icon='🦈',
                layout='wide',
                initial_sidebar_state='expanded')

    default_value_state()
    

    if state.login_status == True:

        pages = {
            'Home': home_page,
            'Settings': settings_page
        }

        # render page
        pages[sidebar(pages)]()
    else:
        login_page()
    


            
    pass


if __name__ == "__main__":
    main()