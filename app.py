import streamlit as st
from login import show_login
from recommender import show_recommender

# Main app logic
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login()  # Show login page if not logged in
else:
    show_recommender()  # Show book recommender page if logged in