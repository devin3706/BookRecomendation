# import pandas as pd
# import pickle
# from pymongo import MongoClient

# # MongoDB connection setup
# MONGODB_URI = 'mongodb+srv://sdevinsilva:JkFboJUEfzMWeJzr@cluster0.m1swz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
# client = MongoClient(MONGODB_URI)

# # Access the database and collection
# db = client['book_recommendation_db']
# books_collection = db['books']
# users_collection = db['users']

# # Load the final ratings dataset from a pickle file
# final_rating = pickle.load(open('artifacts/final_rating.pkl', 'rb'))

# users_to_insert = []

# for user_id in range(1, 11):  # User IDs from 1 to 10
#     user_data = {
#         'user_id': f"user{user_id}",
#         'password': f"pw{user_id}"  # Set password equal to user_id
#     }
#     users_to_insert.append(user_data)

# # Insert users into MongoDB
# if users_to_insert:
#     result = users_collection.insert_many(users_to_insert)
#     print(f"Inserted {len(result.inserted_ids)} users into the MongoDB collection.")
# else:
#     print("No users to insert.")


# # Extract unique books
# # unique_books = final_rating[['title', 'author', 'img_url']].drop_duplicates()

# # # Convert DataFrame to a list of dictionaries
# # books_to_insert = unique_books.to_dict('records')

# # # Insert unique books into MongoDB
# # if books_to_insert:
# #     result = books_collection.insert_many(books_to_insert)
# #     print(f"Inserted {len(result.inserted_ids)} unique books into the MongoDB collection.")
# # else:
# #     print("No unique books to insert.")

# # Close the MongoDB connection
# client.close()