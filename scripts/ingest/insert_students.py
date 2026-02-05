import json
from pathlib import Path
# --------------------
# Connect to MongoDB
# --------------------
import certifi
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os

# --------------------
# Load environment
# --------------------
load_dotenv()  # expects .env in project root
MDB_URI = os.getenv("MDB_CONNECTION_STRING")

if not MDB_URI:
    raise ValueError("MDB_CONNECTION_STRING not found in .env")

# --------------------
# File path
# --------------------
DATA_FILE = Path("data/raw/students_raw.json")
if not DATA_FILE.exists():
    raise FileNotFoundError(f"{DATA_FILE} does not exist. Run generate_students.py first.")



client = MongoClient(
    MDB_URI,
    tls=True,
    tlsCAFile=certifi.where()
)
db = client.arturocluster
collection = db.students_raw

# --------------------
# Load JSON
# --------------------
with open(DATA_FILE, "r") as f:
    students = json.load(f)

# --------------------
# Prepare bulk operations for idempotency
# --------------------
operations = [
    UpdateOne(
        {"student_id": s["student_id"]},  # filter by student_id
        {"$set": s},                       # set all fields
        upsert=True                        # insert if not exists
    )
    for s in students
]

# --------------------
# Execute bulk write
# --------------------
result = collection.bulk_write(operations)
print(f"Inserted: {result.upserted_count}, Modified: {result.modified_count}")
print("Ingestion complete.")
