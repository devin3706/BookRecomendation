import pickle
import streamlit as st
import numpy as np
from pymongo import MongoClient
import pandas as pd

def show_recommender():

    # Load pickled files
    model = pickle.load(open('artifacts/model.pkl', 'rb'))
    book_names = pickle.load(open('artifacts/books_name.pkl', 'rb'))
    final_rating = pickle.load(open('artifacts/final_rating.pkl', 'rb'))
    book_pivot = pickle.load(open('artifacts/book_pivot.pkl', 'rb'))

    # MongoDB connection setup
    MONGODB_URI = 'mongodb+srv://sdevinsilva:JkFboJUEfzMWeJzr@cluster0.m1swz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
    client = MongoClient(MONGODB_URI)

    db = client['book_recommendation_db']
    books_collection = db['books']
    interactions_collection = db['interactions']

    user_id = st.session_state.user_id

    st.title(f"Welcome {user_id}")
    st.header('Book Recommender')

    # Function to get books
    def get_books():
        books = list(books_collection.find())
        return pd.DataFrame(books)

    # Function to add interaction to MongoDB
    def add_interactions(user_id, liked_books, disliked_books):
        interactions = []
        
        # Add liked books
        for book in liked_books:
            interactions.append({
                "user_id": user_id,
                "title": book,
                "Preference": "Like"
            })

        # Add disliked books
        for book in disliked_books:
            interactions.append({
                "user_id": user_id,
                "title": book,
                "Preference": "Dislike"
            })

        if interactions:
            interactions_collection.insert_many(interactions)
            st.success(f"Recorded {len(interactions)} interactions successfully!")

    # Function to retrieve user interactions
    def get_user_interactions(user_id):
        interactions = list(interactions_collection.find({"user_id": user_id}))
        liked_books = [interaction['title'] for interaction in interactions if interaction['Preference'] == "Like"]
        disliked_books = [interaction['title'] for interaction in interactions if interaction['Preference'] == "Dislike"]

        print(f"liked by user {user_id} : {liked_books}")
        print(f"disliked by user {user_id} : {disliked_books}")

        return liked_books, disliked_books

    # Retrieve liked and disliked books from the database
    liked_books_db, disliked_books_db = get_user_interactions(user_id)

    # Assuming final_rating has a column 'author'
    authors_list = final_rating['author'].unique().tolist()

    # Initialize session state variables if they don't exist
    if 'recommended_books' not in st.session_state:
        st.session_state.recommended_books = []
    if 'poster_url' not in st.session_state:
        st.session_state.poster_url = []
    if 'distances' not in st.session_state:
        st.session_state.distances = []

    # Function to fetch poster URLs based on the recommendation
    def fetch_poster(suggestion):
        book_name = []
        ids_index = []
        poster_url = []

        for book_id in suggestion:
            book_name.append(book_pivot.index[book_id])

        for name in book_name[0]:
            ids = np.where(final_rating['title'] == name)[0][0]
            ids_index.append(ids)

        for idx in ids_index:
            url = final_rating.iloc[idx]['img_url']
            poster_url.append(url)

        return poster_url

    # Function to recommend books based on selected book
    def recommend_book(book_name):
        books_list = []
        book_id = np.where(book_pivot.index == book_name)[0][0]
        distance, suggestion = model.kneighbors(book_pivot.iloc[book_id, :].values.reshape(1, -1), n_neighbors=20)

        poster_url = fetch_poster(suggestion)
        
        for i in range(len(suggestion)):
            books = book_pivot.index[suggestion[i]]
            for j in books:
                books_list.append(j)
        
        return books_list, poster_url, distance.flatten()

    # Book Selection and Recommendation
    selected_books = st.selectbox("Type or select a book from the dropdown", book_names)
    selected_authors = st.multiselect("Select authors to filter recommendations", authors_list)

    recommend = st.button('Show Recommendation')

    if recommend:
        recommended_books, poster_url, distances = recommend_book(selected_books)

        # Filter recommendations based on selected authors
        if selected_authors:
            filtered_books = []
            filtered_posters = []
            filtered_distances = []
            
            for idx, book in enumerate(recommended_books):
                book_info = final_rating[final_rating['title'] == book]
                if not book_info.empty and book_info['author'].iloc[0] in selected_authors:
                    filtered_books.append(book)
                    filtered_posters.append(poster_url[idx])
                    filtered_distances.append(distances[idx])
            
            recommended_books, poster_url, distances = filtered_books, filtered_posters, filtered_distances


        filtered_books = []
        filtered_posters = []
        filtered_distances = []

        # First, add liked books to the filtered list
        for book in liked_books_db:
            if book in recommended_books:
                index = recommended_books.index(book)
                filtered_books.append(book)
                filtered_posters.append(poster_url[index])
                filtered_distances.append(distances[index])


        # Filter out disliked books from recommendations
        if disliked_books_db:
            
            for idx, book in enumerate(recommended_books):
                if book not in disliked_books_db and book not in filtered_books:
                    filtered_books.append(book)
                    filtered_posters.append(poster_url[idx])
                    filtered_distances.append(distances[idx])

            recommended_books, poster_url, distances = filtered_books, filtered_posters, filtered_distances
        
        # Store recommendations in session state
        st.session_state.recommended_books = recommended_books
        st.session_state.poster_url = poster_url
        st.session_state.distances = distances

    # Define the number of columns and rows for displaying recommendations
    num_columns = 4
    num_rows = 3

    retrievedBooks = []

    # Create a container for the recommendations if they exist in session state
    if st.session_state.recommended_books:
        
        for row in range(num_rows):
            cols = st.columns(num_columns)

            for col in range(num_columns):
                index = row * num_columns + col
                if index < len(st.session_state.recommended_books):  # Check if index is within range
                    with cols[col]:
                        book_title = st.session_state.recommended_books[index]
                        st.markdown(f"{book_title}")
                        st.image(st.session_state.poster_url[index], use_column_width=True)

                        retrievedBooks.append(book_title)

        likes = st.multiselect("Which Books do you like...", retrievedBooks)
        dislikes = st.multiselect("Which Books do you not like...", retrievedBooks)

        if st.button('Submit Interactions'):
            add_interactions(user_id, likes, dislikes)

    client.close()
