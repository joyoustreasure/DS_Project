import streamlit as st
from pymongo import MongoClient

# MongoDB 연결 설정
secrets = st.secrets["my_mongodb_credentials"]
mongodb_connection_string = secrets["mongodb_connection_string"]
database_name = secrets["database_name"]
collection_name = secrets["collection_name_faq"]

# MongoDB 연결 설정
client = MongoClient(mongodb_connection_string)
db = client[database_name]
collection = db[collection_name]

# MongoDB에서 FAQ 데이터 가져오기
faq_data_from_mongodb = collection.find()

# FAQ 데이터를 딕셔너리로 변환
faq_data = {item['question']: item['answer'] for item in faq_data_from_mongodb}

def create_faq_section():
    st.header('General Question')
    for question, answer in faq_data.items():
        with st.expander(question):
            st.write(answer)
