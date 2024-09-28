import pickle
import streamlit as st
import numpy as np


st.header('Book Recommender System Using Machine Learning')
model = pickle.load(open('artifacts/model.pkl','rb'))
book_names = pickle.load(open('artifacts/books_name.pkl','rb'))
final_rating = pickle.load(open('artifacts/final_rating.pkl','rb'))
book_pivot = pickle.load(open('artifacts/book_pivot.pkl','rb'))


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
    distance, suggestion = model.kneighbors(book_pivot.iloc[book_id,:].values.reshape(1,-1), n_neighbors=15)

    print(suggestion)

    poster_url = fetch_poster(suggestion)
    
    for i in range(len(suggestion)):
            books = book_pivot.index[suggestion[i]]
            for j in books:
                books_list.append(j)
    return books_list , poster_url       



selected_books = st.selectbox(
    "Type or select a book from the dropdown",
    book_names
)

if st.button('Show Recommendation'):
    recommended_books, poster_url = recommend_book(selected_books)

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
                    # Set the height for each container using markdown with HTML
                    st.markdown(
                        f"""
                        <div style="height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                            <div>{recommended_books[index]}</div>
                            <img src="{poster_url[index]}" style="max-height: 150px; width: auto;"/>
                        </div>
                        """,
                        unsafe_allow_html=True)