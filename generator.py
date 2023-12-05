# generator.py

import streamlit as st
import openai
import matplotlib.pyplot as plt
import re

openai.api_key = st.secrets["api_key"]

# 토픽 그룹 목록 정의
topic_groups = [
    ['Computer', 'Internet', 'Information', 'Media', 'Transportation'],
    ['Education', 'School', 'Career'],
    ['Environment', 'Resources', 'Recycling'],
    ['Guide', 'Mail', 'Letter'],
    ['Language', 'Literature', 'Culture'],
    ['Medicine', 'Health', 'Nutrition', 'Food'],
    ['Music', 'Art', 'Movies', 'Dance', 'Photography', 'Architecture'],
    ['Person', 'Anecdote', 'Fable'],
    ['Philosophy', 'Religion', 'History', 'Custom', 'Geography'],
    ['Physics', 'Chemistry', 'Life Science', 'Earth Science'],
    ['Politics', 'Economics', 'Society', 'Law'],
    ['Psychology', 'Interpersonal Relationships'],
    ['Sports', 'Leisure', 'Hobbies', 'Travel']
]

# 문제 생성 함수
def generate_question(topic):
    detailed_prompt = (
        f"Please create a question about {topic} with "
        "multiple-choice options (A), (B), (C), (D), (E) and the correct answer. "
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
    return {
        'question': question_content,
        'options': options,
        'correct_answer': correct_answer
    }

# 문제 파싱 함수
def parse_question_response(response_content):
    lines = response_content.split('\n')
    question_content = ""
    options = []
    correct_answer = ""
    options_start = False
    answer_patterns = [
        re.compile(r"^[A-E]\)"), re.compile(r"^[a-e]\)"),
        re.compile(r"^\([A-E]\)"), re.compile(r"^\([a-e]\)")
    ]

    for line in lines:
        if any(p.match(line) for p in answer_patterns):
            options_start = True
            options.append(line)
        elif line.lower().startswith("correct answer:"):
            correct_answer = line.split(":", 1)[1].strip()
        elif not options_start:
            question_content += line + "\n"

    return question_content.strip(), options, correct_answer

# session_state 초기화 확인
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []

# 메인 함수: 문제 생성 및 네비게이션 관리
def question():
    # 사용자가 토픽 그룹을 선택할 수 있는 selectbox 생성
    group_index = st.selectbox("Choose a topic group to generate questions:", range(len(topic_groups)), format_func=lambda x: ", ".join(topic_groups[x]))
    selected_group = topic_groups[group_index]
    topic_input = st.selectbox("Now select a specific topic:", selected_group)
    left_column, right_column = st.columns([2, 1])

    with left_column:
        if st.button("generate question"):
            if topic_input and len(st.session_state.questions) < 10:  # 10문제 제한 추가
                new_question = generate_question(topic_input)
                st.session_state.questions.append(new_question)
                st.session_state.user_answers.append('')  # 사용자 답변 공간 확보
                st.session_state.current_index = len(st.session_state.questions) - 1

        if 'current_index' in st.session_state and st.session_state.current_index < len(st.session_state.questions):
            current_question = st.session_state.questions[st.session_state.current_index]
            st.write(f"Topic: {st.session_state.current_index + 1}")  # 인덱스로 토픽 번호 표시
            st.write(current_question['question'])
            answer = st.radio("Choose your answer:", current_question['options'], key=f"answer{st.session_state.current_index}")
            st.session_state.user_answers[st.session_state.current_index] = answer

        if len(st.session_state.questions) == 10 and all(st.session_state.user_answers):  # 10문제가 모두 생성되고 답변이 모두 있는 경우
            if st.button("Submit Answers"):
                calculate_score()

    with right_column:
        st.subheader("Saved Questions")
        for i, saved_question in enumerate(st.session_state.questions):
            if st.button(f"Question {i + 1}"):
                st.session_state.current_index = i
                st.experimental_rerun()

def calculate_score():
    score = sum([1 for i in range(len(st.session_state.questions))
                 if st.session_state.questions[i]['correct_answer'] == st.session_state.user_answers[i]])
    st.write(f"You scored {score} out of {len(st.session_state.questions)}")
