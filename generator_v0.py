# generator.py

import streamlit as st
import openai
import matplotlib.pyplot as plt
import re
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

def question():

    # 컬럼 설정: 왼쪽 컬럼을 더 크게 설정합니다.
    left_column, right_column = st.columns([2, 1])
    
    with left_column:
        st.subheader("Welcome to the SAT English Question Generator")
        st.write("Improve your English skills by generating various types of questions.")
        st.write("All data generated here is securely processed to protect your personal information.")

        # 문제 유형, 난이도, 주제를 선택하는 UI
        question_type = st.selectbox("Question Type", ["Single-Word Fill-in-the-Blank", "Phrase Fill-in-the-Blank", "Sequence Inference", "Main Idea Inference"])
        difficulty = st.slider("Vocabulary Difficulty", 1, 5, 2)
        topic = st.text_input("Topic", value="Soccer")
        submit_button = st.button("Generate Question")

        if submit_button:
            generated_question, options, correct_answer = generate_question(question_type, difficulty, topic)
            st.session_state.generated_question = generated_question
            st.session_state.options = options
            st.session_state.correct_answer = correct_answer

        # 문제 생성 결과를 표시하는 UI
        if 'generated_question' in st.session_state:
            st.subheader("Generated Question")
            st.write(st.session_state.generated_question)
            option = st.radio("Options", st.session_state.options)
            submit_answer = st.button("Submit Answer")

            if submit_answer:
                if option == st.session_state.correct_answer:
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect! The correct answer was: {st.session_state.correct_answer}")

    with right_column:
        st.subheader("Saved Questions")
        if 'questions' not in st.session_state:
            st.session_state.questions = []

        # 'Save Question' 버튼을 통해 문제를 저장하는 UI
        if st.button('Save Question') and 'generated_question' in st.session_state:
            st.session_state.questions.append(st.session_state.generated_question)
            st.success("Question saved!")

        # 저장된 문제를 표시하고 관리하는 UI
        for idx, question in enumerate(st.session_state.questions):
            st.text(question)
            col1, col2 = st.columns(2)
            if col1.button('Review', key=f'review{idx}'):
                st.session_state.current_review = question
            if col2.button('Delete', key=f'delete{idx}'):
                st.session_state.questions.pop(idx)
                st.experimental_rerun()
        
        # 선택된 문제를 검토하는 UI
        if 'current_review' in st.session_state:
            st.write(st.session_state.current_review)


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
