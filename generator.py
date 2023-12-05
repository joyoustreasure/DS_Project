# generator.py

import streamlit as st
import openai
import matplotlib.pyplot as plt
import re

openai.api_key = st.secrets["api_key"]

# 문제 생성 함수
def generate_question(topic):
    detailed_prompt = (
        f"Please create a question about {topic} with "
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
    return {
        'question': question_content,
        'options': options,
        'correct_answer': correct_answer
    }

# 문제 파싱 함수
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

    return question_content, options, correct_answer

# session_state 초기화 확인
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'topics' not in st.session_state:
    st.session_state.topics = []
    
# 메인 함수: 문제 생성 및 네비게이션 관리
def question():
    st.title("SAT English Question Generator")
    topic_input = st.text_input("Enter a topic to generate questions:", "")
    # 레이아웃을 위한 컬럼 정의
    left_column, right_column = st.columns([2, 1])

    with left_column:
        # Start 버튼: 새로운 문제 생성
        if st.button("Start"):
            if topic_input:  # 토픽이 입력되었는지 확인
                new_question = generate_question(topic_input)
                st.session_state.questions.append(new_question)
                st.session_state.topics.append(topic_input)  # 토픽 저장
                st.session_state.current_index = len(st.session_state.questions) - 1  # 마지막 문제로 인덱스 설정

        # Next 버튼: 다음 문제로 이동
        if st.button("Next"):
            if 'current_index' in st.session_state:
                if st.session_state.current_index + 1 < len(st.session_state.questions):
                    st.session_state.current_index += 1

        # 현재 문제와 선택지 표시
        if 'current_index' in st.session_state and st.session_state.current_index < len(st.session_state.questions):
            current_question = st.session_state.questions[st.session_state.current_index]
            st.write(f"Topic: {st.session_state.topics[st.session_state.current_index]}")  # 토픽 표시
            st.write(current_question['question'])
            answer = st.radio("Choose your answer:", current_question['options'], key=f"answer{st.session_state.current_index}")
            if 'user_answers' in st.session_state and len(st.session_state.user_answers) > st.session_state.current_index:
                # 이미 답변이 있는 경우 해당 답변을 라디오 버튼에 설정합니다.
                st.session_state.user_answers[st.session_state.current_index] = answer
            else:
                # 새로운 답변을 user_answers에 추가합니다.
                st.session_state.user_answers.append(answer)

    with right_column:
        st.subheader("Saved Questions")
        for i, saved_question in enumerate(st.session_state.questions):
            st.text(saved_question['question'])
            if st.button(f"Delete Question {i+1}", key=f"delete_{i}"):
                del st.session_state.questions[i]
                # 현재 인덱스 조정
                if st.session_state.current_index >= i:
                    st.session_state.current_index -= 1
                st.experimental_rerun()

    # 답변 제출 및 점수 계산
    if 'current_index' in st.session_state and st.session_state.current_index == len(st.session_state.questions) - 1:
        if st.button("Submit Answers"):
            calculate_score()

# Calculate and display the score
def calculate_score():
    score = sum([1 for i in range(len(st.session_state.questions))
                 if st.session_state.questions[i]['correct_answer'] == st.session_state.user_answers[i]])
    st.write(f"You scored {score} out of {len(st.session_state.questions)}")