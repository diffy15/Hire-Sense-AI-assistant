import json
import uuid
from pymongo import MongoClient
from urllib.parse import quote_plus  # For encoding special characters in URI

# Escape special characters in username and password
username = quote_plus("abinaya93004")
password = quote_plus("Abinaya@123")

# MongoDB Connection Setup
MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.rlfliqb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "AI-Hiring"
COLLECTION_NAME = "Candidates"  # Collection will be created automatically if not present

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_candidate_data(candidate_data):
    file_id = str(uuid.uuid4())[:8]
    candidate_data["File ID"] = file_id
    try:
        collection.insert_one(candidate_data)
        print(f"✅ Data saved in MongoDB under {DB_NAME}.{COLLECTION_NAME}")
    except Exception as e:
        print(f"❌ Error saving to MongoDB: {e}")

def load_candidate_data(file_id):
    candidate_data = collection.find_one({"File ID": file_id}, {"_id": 0})
    if candidate_data:
        return candidate_data
    print(f"❌ No data found with File ID: {file_id}")
    return None

def list_all_candidates():
    candidates = collection.find({}, {"full_name": 1, "File ID": 1, "_id": 0})
    return [{"Name": c["full_name"], "File ID": c["File ID"]} for c in candidates]
