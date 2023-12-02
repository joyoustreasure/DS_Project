# generator.py

import streamlit as st
import openai
import matplotlib.pyplot as plt
import re

def question():
    # OpenAI API 키 설정
    openai.api_key = st.secrets["api_key"]

    # 서비스 소개 및 환영 인사
    st.subheader("Welcome!")
    st.write("Welcome to the SAT English question generator.")
    st.write("You can improve your English skills by generating various types of questions.")

    # 개인정보 보호 안내
    st.subheader("Privacy Protection")
    st.write("All data generated here is securely processed to protect your personal information.")

    # 문제 유형 선택 버튼 생성
    st.subheader("Choose Question Type")

    # 문제 생성 요구사항 입력
    with st.expander("Define Question Requirements", expanded=False):
        question_type = st.selectbox("Question Type", ["Blank_Single", "Blank_Multiple", "Sequence", "Main_Idea"])
        difficulty = st.select_slider("Voca Difficulty", options=['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'])
        topic = st.text_input("Topic")
        submit_button = st.button("Submit Requirements")

        # 문제 생성 로직
        if submit_button:
            generated_question, options, correct_answer = generate_question(question_type, difficulty, topic)
            st.session_state['generated_question'] = generated_question
            st.session_state['correct_answer'] = correct_answer
            st.session_state['options'] = options

        # 데이터 수집 및 저장
        if 'question_data' not in st.session_state:
            st.session_state['question_data'] = {'types': [], 'difficulties': [], 'topics': []}
        st.session_state['question_data']['types'].append(question_type)
        st.session_state['question_data']['difficulties'].append(difficulty)
        st.session_state['question_data']['topics'].append(topic if topic else "General")

    # 시각화 기능 추가
    if st.button("Show Question Stats"):
        if 'question_data' in st.session_state:
            visualize_question_data(st.session_state['question_data'])

    # 생성된 문제 및 객관식 답안 선택 표시
    if 'generated_question' in st.session_state and 'options' in st.session_state:
        st.text_area("Generated Question", st.session_state['generated_question'], height=300)
        selected_option = st.radio("Choose an answer", st.session_state['options'])
        submit_answer = st.button("Submit Answer")

        # 답안 제출 및 평가
        if submit_answer:
            if selected_option == st.session_state['correct_answer']:
                st.success("Correct!")
            else:
                st.error("Incorrect! The correct answer was: " + st.session_state['correct_answer'])

        # 문제 저장
        if st.button('Save Question'):
            if 'questions' not in st.session_state:
                st.session_state['questions'] = []
            st.session_state['questions'].append(st.session_state['generated_question'])
            del st.session_state['generated_question']

def generate_question(question_type, difficulty, topic):
    # 객관식 문제 생성 프롬프트
    detailed_prompt = (
        f"Please create a {difficulty} level, {question_type} question about {topic} with "
        "multiple-choice options (A), B), C), D), E)) and the correct answer. "
        "Ensure that the answer choices follow the 5-option multiple-choice format for selection."
    )

    messages = [
        {"role": "system", "content": "You are a high school English test question designer."},
        {"role": "user", "content": detailed_prompt}
    ]

    with st.spinner("Generating question..."):
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response_content = gpt_response['choices'][0]['message']['content']
        question_content, options, correct_answer = parse_question_response(response_content)
    return question_content.strip(), options, correct_answer.strip()

def parse_question_response(response_content):
    # 줄바꿈으로 텍스트를 분리
    lines = response_content.split('\n')
    
    # 문제 내용, 선택지, 정답 초기화
    question_content = ""
    options = []
    correct_answer = ""

    # 선택지 시작을 추적하는 플래그
    options_start = False

    # 가능한 패턴들을 정의
    answer_pattern = re.compile(r"^[A-E]\)")
    answer_pattern_alt = re.compile(r"^[a-e]\)")
    answer_pattern_brackets = re.compile(r"^\([A-E]\)")
    answer_pattern_brackets_alt = re.compile(r"^\([a-e]\)")

    for line in lines:
        if answer_pattern.match(line) or answer_pattern_alt.match(line) or answer_pattern_brackets.match(line) or answer_pattern_brackets_alt.match(line):
            options_start = True
            options.append(line)
        elif line.lower().startswith("correct answer:"):
            correct_answer = line.split(":", 1)[1].strip()
        elif not options_start:
            question_content += line + "\n"

    return question_content.strip(), options, correct_answer


def visualize_question_data(data):
    # 문제 유형별로 카운트 계산 및 시각화
    question_types = list(set(data['types']))
    type_counts = [data['types'].count(t) for t in question_types]

    fig, ax = plt.subplots()
    ax.bar(question_types, type_counts)
    ax.set_title("Question Type Distribution")
    ax.set_xlabel("Question Type")
    ax.set_ylabel("Count")
    st.pyplot(fig)
