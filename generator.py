# generator.py

import streamlit as st
import openai
from mongodb_utils import connect_to_mongodb

# Custom button style with HTML and CSS
def create_custom_button(label, key):
    # Define custom button style
    button_style = f"""
    <style>
        .btn-outline-primary {{
            border: 1px solid #0d6efd;
            color: #0d6efd;
            background-color: transparent;
            background-image: none;
            padding: 0.375rem 0.75rem;
            font-size: 1rem;
            line-height: 1.5;
            border-radius: 0.25rem;
            transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out,
            border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }}
        .btn-custom {{
            display: inline-block;
            width: 100%; /* Full width of the column */
            margin: 0.25rem 0; /* Some margin around the buttons */
            text-align: center;
        }}
    </style>
    <button class="btn btn-outline-primary btn-custom" onclick="handleButtonClick('{key}')">{label}</button>
    <script>
        function handleButtonClick(key) {{
            // Send button click event to Streamlit backend
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                key: key,
                value: true
            }}, '*');
        }}
    </script>
    """
    st.markdown(button_style, unsafe_allow_html=True)

# OpenAI API 키 설정
openai.api_key = st.secrets["api_key"]

# MongoDB 연결
users_collection = connect_to_mongodb("users")

# 난이도 및 특성 관련 데이터 딕셔너리
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

# 문제 유형 딕셔너리
type_dict = {
    "Fill-in-the-Blank-with-Single-Word": 1,
    "Fill-in-the-Blank-with-Phrase":  2,
    "Sequence-Inference": 3,
    "Main-Idea-Inference": 4
}

# 문제 생성에 사용되는 make_prompt 함수 정의
def make_prompt(voca_p, sen_len_p, sen_com_p, group_index):
    prompt_template = {
        1: f'''Please create a Fill-in-the-Blank-with-Single-Word question. 
            The blank should encapsulate the overarching idea presented in the text.
            Voca level should be {voca_p}. 
            The topic should be among {topic_groups[group_index]}.
            There should be {sen_len_p} sentences in the text.
            And the longest sentence of the text should contain {sen_com_p} words.
            Also provide exactly five options for the blank, and indicate the correct answer. Show the answer in Unicode numbers.
            Please insert a line break (\n\n) between the question and the options, and another line break (\n\n) between the options and the answer. Do not include line breaks (\n\n) elsewhere.
            Only five options are required; do not provide more or fewer than five.
            ''',
        
        2: f'''Please create a Fill-in-the-Blank-with-Multiple-Word question.
            The blank should encapsulate the overarching idea presented in the text. 
            Voca level should be {voca_p}. 
            The topic should be among {topic_groups[group_index]}. 
            There should be {sen_len_p} sentences in the text. 
            And the longest sentence of the text should contain {sen_com_p} words. 
            Also provide exactly five options for the blank, and indicate the correct answer. Show the answer in Unicode numbers.
            Please insert a line break (\n\n) between the question and the options, and another line break (\n\n) between the options and the answer. Do not include line breaks (\n\n) elsewhere.
            Only five options are required; do not provide more or fewer than five.
            ''',
        
        3: f'''Please create a sequence-inference question
            Please provide the first two sentences, then divide the remaining text into three parts, with 2-3 sentences in each part. Shuffle them, and ask students to determine the logical sequence.
            Voca level should be {voca_p}. 
            The topic should be among {topic_groups[group_index]}. 
            There should be {sen_len_p} sentences in the text.
            And the longest sentence of the text should contain {sen_com_p} words. 
            Also provide exactly five options for the blank, and indicate the correct answer. Show the answer in Unicode numbers.
            Please insert a line break (\n\n) between the question and the options, and another line break (\n\n) between the options and the answer. Do not include line breaks (\n\n) elsewhere.
            Only five options are required; do not provide more or fewer than five.
            ''',

        4: f'''Please create a Main-Idea-Inference question.
            The answer should encapsulate the overarching idea presented in the text.
            Voca level should be {voca_p}. 
            The topic should be among {topic_groups[group_index]}.
            There should be {sen_len_p} sentences in the text.
            And the longest sentence of the text should contain {sen_com_p} words.
            And the sentence containing blank should carry main idea.
            Also provide exactly five options for the blank, and indicate the correct answer. Show the answer in Unicode numbers.
            Please insert a line break (\n\n) between the question and the options, and another line break (\n\n) between the options and the answer. Do not include line breaks (\n\n) elsewhere.
            Only five options are required; do not provide more or fewer than five.
            '''
    }

    return prompt_template

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

# 문제 번호에 따라 선호도 유형 결정 함수
def get_pref_type(question_number, ranked_preferences):
    if question_number < 4:  # 문제 1-4
        preference_type = ranked_preferences[0]
    elif question_number < 7:  # 문제 5-7
        preference_type = ranked_preferences[1]
    elif question_number < 9:  # 문제 8-9
        preference_type = ranked_preferences[2]
    else:  # 문제 10
        preference_type = ranked_preferences[3]
    return preference_type

# 문제 생성 함수
def generate_question(detailed_prompt, preference_type):
    # GPT에서 날리는 최종 prompt 양식 - detailed_prompt 기반으로 선택
    messages = [
        {"role": "system", "content": "You are a high school English test question designer."},
        {"role": "user", "content": detailed_prompt}
    ]
    with st.spinner("generating question now..."):
        gpt_response = openai.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:personal::8QyMmFNj",
            messages=messages
        )
        response_content = gpt_response.choices[0].message.content
        question_content, options, correct_answer = parse_question_response(response_content)

    return {
        'question': question_content,
        'options': options,
        'correct_answer': correct_answer,
        'question_type': preference_type
    }

def parse_question_response(response_content):
    lines = response_content.split('\n\n')
    question_content = ""
    options = []
    correct_answer = ""

    # 각 섹션을 파싱
    for line in lines:
        # 옵션 섹션 파싱
        if line.startswith('[') and line.endswith(']'):
            # 괄호 안의 내용을 쉼표로 분리하여 옵션 리스트 생성
            options_text = line[1:-1]
            options = [option.strip() for option in options_text.split(',')]
            # 각 옵션 앞에 숫자를 붙임 (①, ②, ...)
            options = [f"① {option}" if i == 0 else f"② {option}" if i == 1 else f"③ {option}" if i == 2 else f"④ {option}" if i == 3 else f"⑤ {option}" for i, option in enumerate(options)]
        elif "①" in line or "②" in line or "③" in line or "④" in line or "⑤" in line:
            correct_answer = line.strip()
        else:
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
    
    # 사용자 이름 가져오기
    username = st.session_state.get('username')
    if not username:
        raise ValueError("No user is currently logged in.")

    # MongoDB에서 사용자 정보를 조회
    user = users_collection.find_one({"username": username})
    if user is None:
        raise ValueError(f"User not found: {username}")
    
    ranked_preferences = user.get("ranked_preferences", [])
    
    group_index = st.selectbox("Choose a topic group to generate questions:", range(len(topic_groups)), format_func=lambda x: ", ".join(topic_groups[x]))
    
    level = level_dict[user["difficulty_level"]]
    topic_coef = coef_dict[group_index]
    level_topic = level - topic_coef

    voca = user["Vocabulary"] / 100 * level_topic / model_coef["Vocabulary"]
    sen_len = user["Sentence Length"] / 100 * level_topic / model_coef["Sentence Length"]
    sen_com = user["Sentence Complexity"] / 100 * level_topic / model_coef["Sentence Complexity"]

    voca_tmp = voca * var_dict["Vocabulary"] + avg_dict["Vocabulary"]
    voca_p = 'hard' if voca_tmp > 0.1228 else 'medium' if voca_tmp > 0.0752 else 'easy'
    sen_len_p = round(sen_len * var_dict["Sentence Length"] + avg_dict["Sentence Length"])
    sen_com_p = round(sen_com * var_dict["Sentence Complexity"] + avg_dict["Sentence Complexity"])

    prompt_template = make_prompt(voca_p, sen_len_p, sen_com_p, group_index) 

    def generate_new_question():
        preference_type = get_pref_type(len(st.session_state.questions), ranked_preferences)
        type_num = type_dict.get(preference_type)
        if type_num is None:
            raise ValueError(f"Invalid question type preference: {preference_type}")
        new_question = generate_question(prompt_template[type_num], preference_type)
        st.session_state.questions.append(new_question)
        st.session_state.user_answers.append('')
        st.session_state.current_index = len(st.session_state.questions) - 1
        st.experimental_rerun()

    left_column, right_column = st.columns([2, 1])

    with left_column:
        # 'Generate Question' 버튼은 'Next Question'과 'Regenerate' 버튼 위에 위치합니다.
        if st.button("Generate Question"):
            if len(st.session_state.questions) < 10: 
                generate_new_question()

        # 질문과 답변 옵션을 보여줍니다.
        if 'current_index' in st.session_state and st.session_state.current_index < len(st.session_state.questions):
            current_question = st.session_state.questions[st.session_state.current_index]
            st.write(f"[Question {st.session_state.current_index + 1}]")
            st.write(current_question['question'])
            options = current_question['options']
            
            # 이전에 저장된 답변을 불러오기
            if st.session_state.current_index < len(st.session_state.user_answers):
                current_answer = st.session_state.user_answers[st.session_state.current_index]
            else:
                current_answer = ''

            # st.radio를 통해 사용자의 현재 선택을 얻기
            selected_option = st.radio(
                "Choose your answer:", 
                options, 
                index=options.index(current_answer) if current_answer in options else 0,
                key=f"answer{st.session_state.current_index}"
            )

            # 선택된 답변을 user_answers 리스트에 저장
            if selected_option and selected_option in options:
                if st.session_state.current_index < len(st.session_state.user_answers):
                    st.session_state.user_answers[st.session_state.current_index] = selected_option
                else:
                    st.session_state.user_answers.append(selected_option)

        # 'Next Question'과 'Regenerate' 버튼을 나란히 배치합니다.
        button_columns = st.columns([1, 1, 1])
        
        with button_columns[0]:  # 'Next Question' 버튼을 왼쪽에 배치합니다.
            if st.button("Next Question"):
                if len(st.session_state.questions) < 10:
                    generate_new_question()

        with button_columns[1]:  # 'Regenerate' 버튼을 오른쪽에 배치합니다.
            if st.button("Regenerate"):
                if len(st.session_state.questions) > 0:
                    st.session_state.questions.pop()  
                    st.session_state.user_answers.pop()
                    st.session_state.current_index = len(st.session_state.questions) - 1
                    if len(st.session_state.questions) < 10: 
                        generate_new_question()

        # 사용자가 모든 문제에 답변하면 'Submit Answers' 버튼을 보여줍니다.
        if len(st.session_state.questions) == 10 and all(st.session_state.user_answers):
            if st.button("Submit Answers"):
                calculate_score()
            

    with right_column:
        st.subheader("Saved Questions")
        for i, saved_question in enumerate(st.session_state.questions):
            if i <9:
                if st.button(f"Question 0{i + 1} created by {username}"):
                    st.session_state.current_index = i
                    st.experimental_rerun()
            else:
                if st.button(f"Question {i + 1} created by {username}"):
                    st.session_state.current_index = i
                    st.experimental_rerun()

def calculate_score():
    # 최종 점수를 받아가는 변수 // 해당 점수를 참고하면 됨.
    score = 0
    for i in range(len(st.session_state.questions)):
        user_answer = st.session_state.user_answers[i].split(' ')[0] if st.session_state.user_answers[i] else ''
        if st.session_state.questions[i]['correct_answer'] == user_answer:
            score += 1
    total_questions = len(st.session_state.questions)
    
    st.write(f"You scored {score} out of {total_questions}", unsafe_allow_html=True)

    # 점수에 따른 진행률 표시줄
    progress = score / total_questions if total_questions else 0
    st.progress(progress)

    # 점수에 따른 색상으로 텍스트 강조
    if score / total_questions >= 0.7:
        color = "green"
        result_message = "Great job!"
    elif score / total_questions >= 0.4:
        color = "orange"
        result_message = "Good effort!"
    else:
        color = "red"
        result_message = "Keep practicing!"

    st.markdown(f"<h2 style='text-align: center; color: {color};'>{result_message}</h2>", unsafe_allow_html=True)

    # 사용자가 70점 이상을 받은 경우
    if score / total_questions >= 0.7:
        username = st.session_state.get('username')
        user_data = users_collection.find_one({"username": username})

        # 현재 난이도를 가져옴. 없으면 Level 1로 가져오는 Logic. 
        current_level = user_data.get("difficulty_level", "Level 1")
        
        # 난이도를 한 단계 올리는 로직
        # 'Level 5'가 최대 난이도라고 가정하고, 그 이상 올라가지 않도록 함.
        if current_level != "Level 5":
            next_level = f"Level {int(current_level.split()[1]) + 1}"
            users_collection.update_one({"username": username}, {"$set": {"difficulty_level": next_level}})
            st.write(f"Congratulations! Your difficulty level has been increased to {next_level}.")
        else:
            st.markdown(f"<h2 style='text-align: center; color: blue;'>Congratulations!</h2>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align: center;'>You have reached the maximum difficulty level. Well done!</h4>", unsafe_allow_html=True)