# FAQ.py

import streamlit as st
from mongodb_utils import connect_to_mongodb

collection = connect_to_mongodb("faq")

# MongoDB에서 FAQ 데이터 가져오기
faq_data_from_mongodb = collection.find()

# FAQ 데이터를 딕셔너리로 변환
faq_data = {item['question']: item['answer'] for item in faq_data_from_mongodb}

def create_faq_section():
    st.header('General Question')
    for question, answer in faq_data.items():
        with st.expander(question):
            st.write(answer)
