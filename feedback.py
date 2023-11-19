import streamlit as st

# 피드백 데이터를 파일로 저장하고 불러오는 함수
def load_feedback():
    try:
        with open("feedback.txt", "r") as file:
            return file.readlines()
    except FileNotFoundError:
        return []

def save_feedback(new_feedback):
    with open("feedback.txt", "a") as file:
        file.write(new_feedback + "\n")

def show_feedback_form():
    with st.form("feedback_form"):
        user_feedback = st.text_area("Share your thoughts:")
        submit_button = st.form_submit_button("Submit Feedback")

        if submit_button and user_feedback:
            save_feedback(user_feedback)
            st.success("Thank you for your feedback!")

def display_feedback_board():
    feedback_list = load_feedback()
    st.write("### User Feedback Board")
    for feedback in feedback_list:
        st.text(feedback)
    