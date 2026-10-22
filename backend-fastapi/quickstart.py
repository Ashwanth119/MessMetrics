from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(
    os.environ["MONGODB_URI"],
    serverSelectionTimeoutMS=10000
)

try:
    print("Connection test:", client.admin.command("ping"))

    db = client["foodfit"]
    db["nutrition_items"].insert_one({
        "name": "besan",
        "calories": 384.7,
        "protein_g": 22.6,
        "serving_size_g": 100
    })

    print("Inserted nutrition data successfully")

finally:
    client.close()