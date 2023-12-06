# Home.py

import streamlit as st
from hashlib import sha256
from generator import question 
from FAQ import create_faq_section
from print import print_exam
import feedback
from account import update_profile_page
from mongodb_utils import connect_to_mongodb

users_collection = connect_to_mongodb("users")

# 페이지 설정
st.set_page_config(
    page_title="Exam Creation Lab",
    page_icon="📚",
    layout='wide'
)

# Insert this at the beginning of your script (after the imports)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

/* General styles */
body {
    font-family: 'Montserrat', sans-serif;
    background-color: #f4f4f4;
    color: #424242;
}

/* Styling for headers */
h1, h2, h3, h4, h5, h6 {
    color: #005792;
    font-weight: 700;
}

h1 {
    font-size: 2.5em; /* 40px */
}

h2 {
    font-size: 2em; /* 32px */
}

h3 {
    font-size: 1.75em; /* 28px */
}

/* Input widgets styling */
.stTextInput, .stSelectbox, .stTextArea {
    border: 2px solid #005792;
    border-radius: 8px;
    padding: 10px;
    font-size: 16px;
    background-color: #ffffff;
    color: #333333;
}

/* Button styling */
.stButton > button {
    border: 2px solid #005792;
    background-color: #005792;
    color: #ffffff;
    font-weight: bold;
    border-radius: 20px;
    padding: 10px 20px;
    font-size: 18px;
    transition: background-color 0.3s, color 0.3s;
}

.stButton > button:hover {
    background-color: #007acc;
    color: #f0f0f0;
}

/* Additional styling for layout and other elements */
.st-bb {
    border-bottom: 2px solid #005792 !important;
}

.st-at {
    color: #005792;
    font-weight: bold;
}

/* Responsive design adjustments */
@media screen and (max-width: 768px) {
    h1 {
        font-size: 2em; /* Adjusted for smaller screens */
    }
}
</style>
""", unsafe_allow_html=True)


# 세션 상태 초기화
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 로그인 상태 확인
def check_login(username, password):
    # Retrieve user information from MongoDB
    user_data = users_collection.find_one({"username": username})

    if user_data and user_data["password"] == sha256(password.encode()).hexdigest():
        st.session_state['username'] = username
        st.session_state['logged_in'] = True
        return True
    return False

def register_user(username, password, Vocabulary, Sentence_Length, Sentence_Complexity, ranked_preferences, difficulty_level):
    hashed_password = sha256(password.encode()).hexdigest()
    # 사용자 정보, 자가 평가 점수 및 순위별 선호도를 데이터베이스에 저장 // Mongo DB에서 아래 Data를 저장
    users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "Vocabulary": Vocabulary,
        "Sentence Length": Sentence_Length,
        "Sentence Complexity": Sentence_Complexity,
        "ranked_preferences": ranked_preferences,
        "difficulty_level": difficulty_level
    })


# 로그인 폼
def login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if check_login(username, password):
                st.success("Successfully logged in.")
                st.session_state['logged_in'] = True 
                st.rerun() 
            else:
                st.error("Incorrect username or password.")

# 회원가입 폼
def register_form():
    with st.form("register_form"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        # User Survey
        st.write("### 1. User Survey")
        question_preference = st.multiselect(
            "Selection of Preferred Question Types: Please list the following question types in order of your interest, starting with the most preferred.",
            ["Fill-in-the-Blank-with-Single-Word", "Fill-in-the-Blank-with-Phrase", "Sequence-Inference", "Main-Idea-Inference"]
        )

        # Create a container to display the ranked preferences
        # This will initially be empty and will be populated upon form submission
        ranked_preferences_container = st.container()

        # Self-assessment of English Proficiency
        st.write("### 2. Evaluation of Desired Problem-Solving Skills Improvement")
        st.write("Please indicate the extent to which you want to improve in the following areas using percentages. Ensure the total adds up to 100%.")
        Vocabulary = st.slider("Vocabulary", 0, 100, 30)
        Sentence_Length = st.slider("Sentence Length", 0, 100, 40)
        Sentence_Complexity = st.slider("Sentence Complexity", 0, 100, 30)
        total_score = Vocabulary + Sentence_Length + Sentence_Complexity

        # Choose the difficulty level of starting problem solving
        st.write("### 3. Choose the difficulty level of starting problem solving")
        difficulty_level = st.selectbox(
            "Select your preferred difficulty level:",
            ("Level 1", "Level 2", "Level 3", "Level 4", "Level 5")
        )

        submit_button = st.form_submit_button("Sign Up")

        if submit_button:
            existing_user = users_collection.find_one({"username": new_username})
            if not new_username or not new_password or not confirm_password:
                st.error("Please fill out all fields.")
            elif existing_user:
                st.error("This username is already taken. Please choose a different one.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(question_preference) != 4:
                st.error("Please select your preferences before signing up.")
            else:
                # Rank the preferences based on user selection
                ranked_preferences = {}
                for i, pref in enumerate(question_preference):
                    ranked_preferences[pref] = i + 1
                ranked_preferences_list = [pref for pref, _ in sorted(ranked_preferences.items(), key=lambda item: item[1])]

                # Check if total score is 100
                if total_score == 100:
                    # Save user information and self-assessment scores to the database
                    register_user(new_username, new_password, Vocabulary, Sentence_Length, Sentence_Complexity, ranked_preferences_list, difficulty_level)
                    st.success("Your account has been successfully created. You can now log in.")
                    
                    # Display the ranked preferences
                    with ranked_preferences_container:
                        st.write("#### Your ranked preferences")
                        for pref, rank in sorted(ranked_preferences.items(), key=lambda item: item[1]):
                            st.write(f"Rank {rank}: {pref}")
                else:
                    st.error("Total score must be 100 points. Please adjust it.")


# 로그인 상태가 아니면 로그인 폼을 보여줌
if not st.session_state['logged_in']:
    login_or_register = st.radio("Choose an option", ["Login", "Register"])
    if login_or_register == "Login":
        login_form()
    elif login_or_register == "Register":
        register_form()
else:
    # 로그인 후, 사이드바 메뉴 옵션을 보여줍니다.
    st.sidebar.title("Menu")
    app_choice = st.sidebar.radio(
        "Choose the App", 
        ["Home 🏡", "Create Questions 📝", "Print Exam 🖨️", "Frequently Asked Questions ❓", "Question Type Examples 📚", "User Feedback 🗣️", "Update Profile 🔑"]
    )

    # 홈 화면 내용을 표시합니다.
    if app_choice == "Home 🏡":
        
        st.title("👩‍🏫 3355's Exam Creation Lab!")
        st.markdown("Empowering English Educators")
        st.markdown("Welcome, dedicated educators! Our Exam Creation Lab is specifically designed to assist you in crafting comprehensive English exams. With our platform, you can easily generate various types of questions that cater to all aspects of language learning.")
        
        # 최근 업데이트 및 공지사항 섹션
        st.subheader("📢 Recent Updates & Announcements")
        st.markdown("🆕 **New Feature**: Now you can use features for user feedback.")
        st.markdown("📅 **Upcoming Event**: Join us on preparing 3355's show case")
        st.markdown("🔔 **Reminder**: Don't forget to final test day")

        st.subheader("Diverse Question Types")
        st.write("Dive into a plethora of question types ranging from grammar-focused fill-in-the-blanks to critical thinking multiple-choice questions. Our system supports creating questions for reading comprehension, vocabulary enhancement, and writing proficiency.")
        st.subheader("Maximizing Study Outcomes")
        st.write("To get the most out of your exams, we recommend using a blend of question types to challenge different cognitive skills. Encourage students to practice with timed quizzes for speed, and longer, reflective questions for deep learning. Mix and match to customize the perfect exam!")
        st.subheader("Your Partner in Education")
        st.write("We are here to support you in nurturing the next generation of English speakers. Utilize our platform to enhance your teaching strategy, engage your students, and watch their language skills flourish.")

    # 다른 메뉴 옵션의 경우 해당 기능을 실행합니다.
    elif app_choice == "Create Questions 📝":
        st.title("📘 CSAT English Question Generator")
        question()
    elif app_choice == "Print Exam 🖨️":
        st.title("🖨️ Print Exam")
        st.write("Review and print your created exam.")
        print_exam()
    elif app_choice == "Frequently Asked Questions ❓":
        st.title("❓ Frequently Asked Questions")
        st.write("Find answers to common questions.")
        create_faq_section()

    elif app_choice == "Question Type Examples 📚":
        st.title("📚 Question Type Examples")
        st.write("Explore different types of questions you can create.")
        container1 = st.container()
        container1.write("#### Sequence")
        container1.write("According to the market response model, it is increasing prices that drive providers to search for new sources, innovators to substitute, consumers to conserve, and alternatives to emerge. ")
        container1.write("(A) Many examples of such “green taxes” exist. Facing landfill costs, labor expenses, and related costs in the provision of garbage disposal, for example, some cities have required households to dispose of all waste in special trash bags, purchased by consumers themselves, and often costing a dollar or more each.")
        container1.write("(B) Taxing certain goods or services, and so increasing prices, should result in either decreased use of these resources or creative innovation of new sources or options. The money raised through the tax can be used directly by the government either to supply services or to search for alternatives.")
        container1.write("(C) The results have been greatly increased recycling and more careful attention by consumers to packaging and waste. By internalizing the costs of trash to consumers, there has been an observed decrease in the flow of garbage from households.")
        st.write("① (A) - (C) - (B)")
        st.write("② (B) - (A) - (C)")
        st.write("③ (B) - (C) - (A)")
        st.write("④ (C) - (A) - (B)")
        st.write("⑤ (C) - (B) - (A)")

        container2 = st.container()
        container2.write("### Blank_Sentence")
        container2.write("Precision and determinacy are a necessary requirement for all meaningful scientific debate, and progress in the sciences is, to a large extent, the ongoing process of achieving ever greater precision. But historical representation puts a premium on a proliferation of representations, hence not on the refinement of one representation but on the production of an ever more varied set of representations. Historical insight is not a matter of a continuous “narrowing down” of previous options, not of an approximation of the truth, but, on the contrary, is an “explosion” of possible points of view. It therefore aims at the unmasking of previous illusions of determinacy and precision by the production of new and alternative representations, rather than at achieving truth by a careful analysis of what was right and wrong in those previous representations. And from this perspective, the development of historical insight may indeed be regarded by the outsider as a process of creating ever more confusion, a continuous questioning of [BLANK], rather than, as in the sciences, an ever greater approximation to the truth.")
        st.write("① criteria for evaluating historical representations")
        st.write("② certainty and precision seemingly achieved already")
        st.write("③ possibilities of alternative interpretations of an event")
        st.write("④ coexistence of multiple viewpoints in historical writing")
        st.write("⑤ correctness and reliability of historical evidence collected")

        container3 = st.container()
        container3.write("### Blank_Word")         
        container3.write("Humour involves not just practical disengagement but cognitive disengagement. As long as something is funny, we are for the moment not concerned with whether it is real or fictional, true or false. This is why we give considerable leeway to people telling funny stories. If they are getting extra laughs by exaggerating the silliness of a situation or even by making up a few details, we are happy to grant them comic licence, a kind of poetic licence. Indeed, someone listening to a funny story who tries to correct the teller ― ‘No, he didn’t spill the spaghetti on the keyboard and the monitor, just on the keyboard’ ― will probably be told by the other listeners to stop interrupting. The creator of humour is putting ideas into people’s heads for the pleasure those ideas will bring, not to provide [BLANK] information.")
        st.write("① accurate")
        st.write("② detailed")
        st.write("③ useful")
        st.write("④ additional")
        st.write("⑤ alternative")

        container4 = st.container()
        container4.write("### Flow")       
        container4.write("Since their introduction, information systems have substantially changed the way business is conducted. ① This is particularly true for business in the shape and form of cooperation between firms that involves an integration of value chains across multiple units. ② The resulting networks do not only cover the business units of a single firm but typically also include multiple units from different firms. ③ As a consequence, firms do not only need to consider their internal organization in order to ensure sustainable business performance; they also need to take into account the entire ecosystem of units surrounding them. ④ Many major companies are fundamentally changing their business models by focusing on profitable units and cutting off less profitable ones. ⑤ In order to allow these different units to cooperate successfully, the existence of a common platform is crucial.")
    # 사용자 피드백 메뉴 옵션 처리
    elif app_choice == "User Feedback 🗣️":
        st.title("🗣️ User Feedback")
        feedback.show_satisfaction_survey()
        feedback.show_feedback_form()
        #feedback.display_feedback_board()
        feedback.display_feedback_board()
    elif app_choice == "Update Profile 🔑":
        st.title("🔑 Update your Profile")
        update_profile_page()