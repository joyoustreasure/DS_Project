import streamlit as st
from hashlib import sha256
from generator import question  # 예시로 generator.py 파일에서 create_question 함수를 임포트합니다.
from FAQ import create_faq_section  # 예시로 Eng.py 파일에서 create_faq_section 함수를 임포트합니다.
from print import print_exam

# 페이지 설정
st.set_page_config(
    page_title="Exam Creation Lab",
    page_icon="📚"
)

# 사용자 정보 (실제 환경에서는 안전하게 관리해야 함)
users = {
    "user1": sha256("password1".encode()).hexdigest(),
    "user2": sha256("password2".encode()).hexdigest()
}

# 세션 상태 초기화
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# 로그인 상태 확인
def check_login(username, password):
    if username in users and users[username] == sha256(password.encode()).hexdigest():
        st.session_state['username'] = username
        st.session_state['logged_in'] = True
        return True
    return False

# 로그인 폼
def login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if check_login(username, password):
                st.success("Successfully logged in.")
                st.session_state['logged_in'] = True  # 로그인 상태를 세션 상태에 저장
                st.experimental_rerun()  # 스크립트를 재실행합니다.
            else:
                st.error("Incorrect username or password.")

# 로그인 상태가 아니면 로그인 폼을 보여줌
if not st.session_state['logged_in']:
    login_form()
else:
    # 로그인 후, 사이드바 메뉴 옵션을 보여줍니다.
    st.sidebar.title("Menu")
    app_choice = st.sidebar.radio(
        "Choose the App", 
        ["Home 🏡", "Create Questions 📝", "Print Exam 🖨️", "Frequently Asked Questions ❓", "Question Type Examples 📚"]
    )

    # 홈 화면 내용을 표시합니다.
    if app_choice == "Home 🏡":
        st.image("2.jpg")
        st.title("👩‍🏫 3355's Exam Creation Lab!")
        st.markdown("Empowering English Educators")
        st.markdown("Welcome, dedicated educators! Our Exam Creation Lab is specifically designed to assist you in crafting comprehensive English exams. With our platform, you can easily generate various types of questions that cater to all aspects of language learning.")
        st.subheader("Diverse Question Types")
        st.write("Dive into a plethora of question types ranging from grammar-focused fill-in-the-blanks to critical thinking multiple-choice questions. Our system supports creating questions for reading comprehension, vocabulary enhancement, and writing proficiency.")
        st.subheader("Maximizing Study Outcomes")
        st.write("To get the most out of your exams, we recommend using a blend of question types to challenge different cognitive skills. Encourage students to practice with timed quizzes for speed, and longer, reflective questions for deep learning. Mix and match to customize the perfect exam!")
        st.subheader("Your Partner in Education")
        st.write("We are here to support you in nurturing the next generation of English speakers. Utilize our platform to enhance your teaching strategy, engage your students, and watch their language skills flourish.")
        

    # 다른 메뉴 옵션의 경우 해당 기능을 실행합니다.
    elif app_choice == "Create Questions 📝":
        question()
    elif app_choice == "Print Exam 🖨️":
        st.title("🖨️ Print Exam")
        st.write("Review and print your created exam.")
        print_exam()
    elif app_choice == "Frequently Asked Questions ❓":
        st.title("❓ Frequently Asked Questions")
        st.write("Find answers to common questions.")
        create_faq_section()
    # 희진아 여기에 example을 추가해라
    # 희진아 일요일 18시까지 해라.
    elif app_choice == "Question Type Examples 📚":
        st.title("📚 Question Type Examples")
        st.write("Explore different types of questions you can create.")
