# feedback.py

import streamlit as st
from pymongo import MongoClient
from mongodb_utils import connect_to_mongodb

feedback_collection = connect_to_mongodb("feedback")

# 세션 상태 초기화
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 피드백 데이터를 MongoDB에서 불러오는 함수
def load_feedback():
    feedback_list = feedback_collection.find()
    return [feedback["content"] for feedback in feedback_list]

# 피드백을 MongoDB에 저장하는 함수
def save_feedback(username, new_feedback):
    feedback_data = {
        "username": username,
        "content": new_feedback
    }
    feedback_collection.insert_one(feedback_data)

def show_feedback_form():
    with st.form("feedback_form"):
        st.write("### User Feedback")
        user_feedback = st.text_area("Share your thoughts:")
        submit_button = st.form_submit_button("Submit Feedback")

        if submit_button and user_feedback:
            save_feedback(st.session_state['username'], user_feedback)
            st.success("Thank you for your feedback!")

def show_satisfaction_survey():
    with st.form("satisfaction_survey"):
        st.write("### Satisfaction Survey")
        rating = st.slider("How satisfied are you with our service?", 1, 10, 2)
        #comments = st.text_area("Additional comments:")
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            satisfaction_feedback = f"Satisfaction Rating: {rating}"
            save_feedback(st.session_state['username'], satisfaction_feedback)
            st.success("Thank you for your feedback!")

def display_feedback_board():
    feedback_list = load_feedback()
    st.write("### User Feedback Board")
    for feedback in feedback_list:
        st.text(feedback)
    