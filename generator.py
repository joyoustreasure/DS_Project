# generator.py

import streamlit as st
import openai
import matplotlib.pyplot as plt
import re
from mongodb_utils import connect_to_mongodb

openai.api_key = st.secrets["api_key"]
users_collection = connect_to_mongodb("users")

level_dict = {"Level 1": 0.45, "Level 2": 0.55, "Level 3": 0.65, "Level 4": 0.75, "Level 5": 0.85}
cur_dict = {"Vocabulary": 50, "Sentence Length": 10, "Sentence Complexity": 30}
coef_dict = {0: 1.140186372865045,
            1: 0.4090126220153971,
            2: 0.667917318420521,
            3: -3.912455154502394,
            4: 0.843169559579797,
            5: 0.09850008527767296,
            6: 0.5176263343330191,
            7: 1.3226536105030031,
            8: 1.095391025960897,
            9: 0.749324100073369,
            10: 1.738140724292267,
            11: 0.14804538327885708,
            12: 0.826669197243807}
avg_dict = {"Vocabulary": 0.09490007996883483, "Sentence Length": 10.170168067226891, "Sentence Complexity":34.49579831932773}
var_dict = {"Vocabulary": 0.043720581187843624, "Sentence Length": 5.238564766593916, "Sentence Complexity":9.769662128148886}
model_coef = {"Vocabulary":  0.09099283, "Sentence Length": -0.82754087,  "Sentence Complexity": 0.03954835}

type_dict = {
    "Fill-in-the-Blank-with-Single-Word": 1,
    "Fill-in-the-Blank-with-Phrase":  2,
    "Sequence-Inference": 3,
    "Main-Idea-Inference": 4
}

def make_prompt(username, type_num, group_index):
    user = users_collection.find_one({"username": username})
    level = level_dict[user["difficulty_level"]]
    topic_coef = coef_dict[group_index]
    level_topic = level - topic_coef

    # hard >1.228 medium >=0.0752 easy 
    voca = user["Vocabulary"] / 100 * level_topic / model_coef["Vocabulary"] 
    sen_len = user["Sentence Length"] / 100 * level_topic / model_coef["Sentence Length"]
    sen_com = user["Sentence Complexity"] / 100 * level_topic / model_coef["Sentence Complexity"]        
    
    voca_tmp = voca * var_dict["Vocabulary"] + avg_dict["Vocabulary"]
    voca_p = 'hard' if voca_tmp > 0.1228 else 'medium' if voca_tmp > 0.0752 else 'easy'
    sen_len_p = round(sen_len * var_dict["Sentence Length"] + avg_dict["Sentence Length"])
    sen_com_p  = round(sen_com * var_dict["Sentence Complexity"] + avg_dict["Sentence Complexity"])

    if type_num == 1:
        prompt = f'Please create a Fill-in-the-Blank-with-Single-Word question. 
        The blank should encapsulate the overarching idea presented in the text.
        Voca level should be {voca_p}. 
        The topic should be among {topic_groups[group_index]}.
        There should be {sen_len_p} sentences in the text.
        And the longest sentence of the text should contain {sen_com_p} words.
        Also provide five options, and correct answer.'
    
    elif type_num == 2:
        prompt = f'Please create a Fill-in-the-Blank-with-Multiple-Word question.
        The blank should encapsulate the overarching idea presented in the text. 
        Voca level should be {voca_p}. 
        The topic should be among {topic_groups[group_index]}. 
        There should be {sen_len_p} sentences in the text. 
        And the longest sentence of the text should contain {sen_com_p} words. 
        Also provide five options, and correct answer.'
    
    elif type_num == 3:
        prompt = f'Please create a sequence-inference question
        Please provide the first two sentences, then divide the remaining text into three parts, with 2-3 sentences in each part. Shuffle them, and ask students to determine the logical sequence.
        Voca level should be {voca_p}. 
        The topic should be among {topic_groups[group_index]}. 
        There should be {sen_len_p} sentences in the text.
        And the longest sentence of the text should contain {sen_com_p} words. 
        Also provide five options, and correct answer.'

    else:
        prompt = f'Please create a Main-Idea-Inference question.
        The answer should encapsulate the overarching idea presented in the text.
        Voca level should be {voca_p}. 
        The topic should be among {topic_groups[group_index]}.
        There should be {sen_len_p} sentences in the text.
        And the longest sentence of the text should contain {sen_com_p} words.
        And the sentence containing blank should carry main idea.
        Also provide five options, and correct answer.'

    return prompt

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
        "multiple-choice options ①, ②, ③, ④, ⑤ and the correct answer. "
        "Ensure that the answer choices follow the 5-option multiple-choice format for selection."
    )

    messages = [
        {"role": "system", "content": "You are a high school English test question designer."},
        {"role": "user", "content": detailed_prompt}
    ]

    with st.spinner("Generating question..."):
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # fine tunning : ft:gpt-3.5-turbo-1106:personal::8SR52ebu
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
        re.compile(r"^\u2460"),  # ①
        re.compile(r"^\u2461"),  # ②
        re.compile(r"^\u2462"),  # ③
        re.compile(r"^\u2463"),  # ④
        re.compile(r"^\u2464")   # ⑤
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
    st.session_state.user_answers = []  # This should be a list, as you are accessing it by index

# 메인 함수: 문제 생성 및 네비게이션 관리
def question():
    group_index = st.selectbox("Choose a topic group to generate questions:", range(len(topic_groups)), format_func=lambda x: ", ".join(topic_groups[x]))
    selected_group = topic_groups[group_index]
    topic_input = st.selectbox("Now select a specific topic:", selected_group)
    left_column, right_column = st.columns([2, 1])

    with left_column:
        if st.button("Generate Question"):
            if topic_input and len(st.session_state.questions) < 10:  # 10문제 제한
                new_question = generate_question(topic_input)
                st.session_state.questions.append(new_question)
                st.session_state.user_answers.append('')  # Append an empty string for each new question
                st.session_state.current_index = len(st.session_state.questions) - 1


        if 'current_index' in st.session_state and st.session_state.current_index < len(st.session_state.questions):
            current_question = st.session_state.questions[st.session_state.current_index]
            st.write(f"Topic: {st.session_state.current_index + 1}")
            st.write(current_question['question'])
            options = current_question['options']
            
            # Directly access the user_answers list by index with proper bounds checking
            if st.session_state.current_index < len(st.session_state.user_answers):
                current_answer = st.session_state.user_answers[st.session_state.current_index]
            else:
                current_answer = ''
                
            # Find the index of the current answer in the options list
            answer_index = options.index(current_answer) if current_answer in options else 0
            answer = st.radio(
                "Choose your answer:", 
                options, 
                index=answer_index, 
                key=f"answer{st.session_state.current_index}"
            )
            # Save the selected answer to the user_answers list
            if st.session_state.current_index < len(st.session_state.user_answers):
                st.session_state.user_answers[st.session_state.current_index] = answer

        if len(st.session_state.questions) == 10 and all(st.session_state.user_answers.values()):
            if st.button("Submit Answers"):
                calculate_score()

        if st.button("Next Question"):
            if len(st.session_state.questions) < 10:
                new_question = generate_question(topic_input)
                st.session_state.questions.append(new_question)
                st.session_state.user_answers.append('')
                st.session_state.current_index = len(st.session_state.questions) - 1
                st.experimental_rerun()

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
