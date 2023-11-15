import streamlit as st
import openai


def question():
    # OpenAI API 키를 설정합니다.
    openai.api_key = st.secrets["api_key"]

    # Set the web page title.
    st.title("📘 SAT English Question Generator")

    # Deliver the service introduction and welcome greeting to the user.
    st.subheader("Welcome!")
    st.write("Welcome to the SAT English question generator.")
    st.write("You can improve your English skills by generating various types of questions.")
    st.write("")
    
    # Provide guidance on privacy protection.
    st.subheader("Privacy Protection")
    st.write("All data generated here is securely processed to protect your personal information.")

    # Create buttons for each question type, with icons.
    st.subheader("Choose Question Type")

    # 문제 생성 요구사항 입력
    with st.expander("Define Question Requirements", expanded=False):
        question_type = st.selectbox("Question Type", ["Fill-in-the-Blank", "Multiple Choice", "True/False"])
        difficulty = st.select_slider("Voca Difficulty", options=['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'])
        topic = st.text_input("Topic")
        submit_button = st.button("Submit Requirements")

    # 문제 생성 로직
    if submit_button:
        generated_question = generate_question(question_type, difficulty, topic)
        st.session_state['generated_question'] = generated_question

    # 생성된 문제 표시 및 저장 로직
    if 'generated_question' in st.session_state:
        st.text_area("Generated Question", st.session_state['generated_question'], height=300)
        if st.button('Save Question'):
            if 'questions' not in st.session_state:
                st.session_state['questions'] = []
            st.session_state['questions'].append(st.session_state['generated_question'])
            del st.session_state['generated_question']  # 현재 생성된 문제 삭제
            st.success("Question saved successfully!")

def generate_question(question_type, difficulty, topic):
    # 문제 유형, 난이도, 주제에 따른 세부적인 프롬프트 생성
    detailed_prompt = f"Please create a {difficulty} level, {question_type} question about {topic}. Also provide four options and the correct answer."

    # 시스템 메시지와 사용자의 세부적인 프롬프트를 설정합니다.
    messages = [
        {"role": "system", "content": "You are a high school English test question designer."},
        {"role": "user", "content": detailed_prompt}
    ]

    with st.spinner("Generating question..."):
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
    return gpt_response['choices'][0]['message']['content']



    