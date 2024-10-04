import pickle
import streamlit as st
import numpy as np
import sklearn

st.header('Book Recommender System Using Machine Learning')
model = pickle.load(open('artifacts/model.pkl', 'rb'))
book_names = pickle.load(open('artifacts/books_name.pkl', 'rb'))
final_rating = pickle.load(open('artifacts/final_rating.pkl', 'rb'))
book_pivot = pickle.load(open('artifacts/book_pivot.pkl', 'rb'))

# Assuming final_rating has a column 'author'
authors_list = final_rating['author'].unique().tolist()

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

def recommend_book(book_name):
    books_list = []
    book_id = np.where(book_pivot.index == book_name)[0][0]
    distance, suggestion = model.kneighbors(book_pivot.iloc[book_id, :].values.reshape(1, -1), n_neighbors=100)

    poster_url = fetch_poster(suggestion)
    
    for i in range(len(suggestion)):
        books = book_pivot.index[suggestion[i]]
        for j in books:
            books_list.append(j)
    return books_list, poster_url, distance.flatten()

selected_books = st.selectbox("Type or select a book from the dropdown", book_names)

# Multiselect box for authors
selected_authors = st.multiselect("Select authors to filter recommendations", authors_list)

if st.button('Show Recommendation'):
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

    # Define the number of columns and rows
    num_columns = 4
    num_rows = 3

    # Create a container for the recommendations
    for row in range(num_rows):
        cols = st.columns(num_columns)

        for col in range(num_columns):
            index = row * num_columns + col
            if index < len(recommended_books):  # Check if index is within range
                with cols[col]:
                    
                    print(f"{recommended_books[index]} \t:\t{distances[index]}")

                    # Set the height for each container using markdown with HTML
                    st.markdown(
                        f"""
                        <div style="height: 250px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                            <div>{recommended_books[index]}</div>
                            <img src="{poster_url[index]}" style="max-height: 200px; width: auto;"/>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )