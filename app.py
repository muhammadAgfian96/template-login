import streamlit as st
from state_management import *

from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
from streamlit.hashing import _CodeHasher

from pages.login import *
from pages.home import home_page
from pages.settings import settings_page
from pages.register import div_register


def sidebar(pages):
    st.sidebar.write('## Navigation')
    sel_page = st.sidebar.radio('to', list(pages.keys()))
    return sel_page

def logout(state):
    state.login_status = False
    state.clear()

def main():
    st.set_page_config(page_title='Rat Damage', page_icon='🌴', layout='wide', initial_sidebar_state='expanded')
    state = _get_state()
    default_value_state(state)

    if state.login_status == True:
        col = st.beta_columns((1,1,1,1,1,1))
        # state.user.name
        # state.user.role
        # state.user.status

        if col[-1].button('Logout'):
            state.login_status = False
            state.clear()
        
        col[-1].write(f'Hi, **{state.user.name}**')
        col[-1].write(f'Status: **{"Active" if state.user.status else "Non Active"}**')

        if state.user.status == False:
            st.error('# Sorry, Check your status!')
            return
            
        # here your template to apply
        pages = {
            'Home': home_page,
            'Settings': settings_page
        }

        if state.user.role == 'superuser':
            pages['Register User'] = div_register

        # render page
        pages[sidebar(pages)](state)
    else:
        login_page(state)
        # div_register(state, roles=['grader', 'admin', 'superuser'])



    st.write('End Page')
    state.sync()
# -------------- FOR STATE MANAGEMENT -----------------

class _SessionState:
    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)
    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value
    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()
    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False
        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


if __name__ == "__main__":
    main()