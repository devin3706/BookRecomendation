import streamlit as st
from pymongo import MongoClient

# MongoDB connection setup


def show_login():
    st.title("Login Page")

    MONGODB_URI = 'mongodb+srv://sdevinsilva:JkFboJUEfzMWeJzr@cluster0.m1swz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
    client = MongoClient(MONGODB_URI)
    db = client['book_recommendation_db']
    users_collection = db['users']
    
    user_id = st.text_input("User ID", "")
    password = st.text_input("Password", "", type="password")

    if st.button("Login"):
        user = users_collection.find_one({"user_id": user_id, "password": password})
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
            st.success("Login successful!")
            st.rerun()  # Reload the app to show the recommender page
        else:
            st.error("Invalid credentials. Please try again.")

    client.close()