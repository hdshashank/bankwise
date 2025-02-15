from pymongo import MongoClient

# Directly add MongoDB connection string
MONGO_URI = "mongodb://localhost:27017/"

client = MongoClient(MONGO_URI)
db = client["emails"]  # Replace 'emails' with your actual database name
users_collection = db["emails_attach"]  # Replace 'emails_attach' with your actual collection name
