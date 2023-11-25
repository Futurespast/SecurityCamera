from pymongo import MongoClient
from gridfs import GridFS

def get_database():
    client = MongoClient("mongodb+srv://Mvacc:pwd@iotproject.lkfss1w.mongodb.net/?retryWrites=true&w=majority")
    db = client.your_database_name
    return db

def get_gridfs(db):
    return GridFS(db)
