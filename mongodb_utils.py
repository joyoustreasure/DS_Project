from pymongo import MongoClient
import streamlit as st

def connect_to_mongodb(collection_name):
    secrets = st.secrets["my_mongodb_credentials"]
    mongodb_connection_string = secrets["mongodb_connection_string"]
    database_name = secrets["database_name"]

    client = MongoClient(mongodb_connection_string)
    db = client[database_name]
    collection = db[collection_name]

    return collection