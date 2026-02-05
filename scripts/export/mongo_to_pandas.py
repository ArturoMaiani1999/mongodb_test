# scripts/export/mongo_to_pandas.py
import pandas as pd
from pymongo import MongoClient
import certifi, os
from dotenv import load_dotenv

load_dotenv()
MDB_URI = os.getenv("MDB_CONNECTION_STRING")

client = MongoClient(MDB_URI, tls=True, tlsCAFile=certifi.where())
db = client.arturocluster

df = pd.DataFrame(list(db.students_features.find({}, {"_id": 0})))
print(df.head())
df.to_csv("data/derived/students_features.csv", index=False)
