import streamlit as st
from hashlib import sha256
from generator import question 
from FAQ import create_faq_section
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
                st.rerun()  # 스크립트를 재실행합니다.
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
        st.write("--Sequence--")
        st.write("According to the market response model, it is increasing prices that drive providers to search for new sources, innovators to substitute, consumers to conserve, and alternatives to emerge. ")
        st.write("(A) Many examples of such “green taxes” exist. Facing landfill costs, labor expenses, and related costs in the provision of garbage disposal, for example, some cities have required households to dispose of all waste in special trash bags, purchased by consumers themselves, and often costing a dollar or more each.")
        st.write("(B) Taxing certain goods or services, and so increasing prices, should result in either decreased use of these resources or creative innovation of new sources or options. The money raised through the tax can be used directly by the government either to supply services or to search for alternatives.")
        st.write("(C) The results have been greatly increased recycling and more careful attention by consumers to packaging and waste. By internalizing the costs of trash to consumers, there has been an observed decrease in the flow of garbage from households.")

        st.write("--Blank_Sentence--")
        st.write("Precision and determinacy are a necessary requirement for all meaningful scientific debate, and progress in the sciences is, to a large extent, the ongoing process of achieving ever greater precision. But historical representation puts a premium on a proliferation of representations, hence not on the refinement of one representation but on the production of an ever more varied set of representations. Historical insight is not a matter of a continuous “narrowing down” of previous options, not of an approximation of the truth, but, on the contrary, is an “explosion” of possible points of view. It therefore aims at the unmasking of previous illusions of determinacy and precision by the production of new and alternative representations, rather than at achieving truth by a careful analysis of what was right and wrong in those previous representations. And from this perspective, the development of historical insight may indeed be regarded by the outsider as a process of creating ever more confusion, a continuous questioning of [BLANK], rather than, as in the sciences, an ever greater approximation to the truth.")
        st.write("① criteria for evaluating historical representations")
        st.write("② certainty and precision seemingly achieved already")
        st.write("③ possibilities of alternative interpretations of an event")
        st.write("④ coexistence of multiple viewpoints in historical writing")
        st.write("⑤ correctness and reliability of historical evidence collected")

        st.write("--Blank_Word--")
        st.write("Humour involves not just practical disengagement but cognitive disengagement. As long as something is funny, we are for the moment not concerned with whether it is real or fictional, true or false. This is why we give considerable leeway to people telling funny stories. If they are getting extra laughs by exaggerating the silliness of a situation or even by making up a few details, we are happy to grant them comic licence, a kind of poetic licence. Indeed, someone listening to a funny story who tries to correct the teller ― ‘No, he didn’t spill the spaghetti on the keyboard and the monitor, just on the keyboard’ ― will probably be told by the other listeners to stop interrupting. The creator of humour is putting ideas into people’s heads for the pleasure those ideas will bring, not to provide [BLANK] information.")
        st.write("① accurate")
        st.write("② detailed")
        st.write("③ useful")
        st.write("④ additional")
        st.write("⑤ alternative")


        st.write("--Flow--")
        st.write("Since their introduction, information systems have substantially changed the way business is conducted. ① This is particularly true for business in the shape and form of cooperation between firms that involves an integration of value chains across multiple units. ② The resulting networks do not only cover the business units of a single firm but typically also include multiple units from different firms. ③ As a consequence, firms do not only need to consider their internal organization in order to ensure sustainable business performance; they also need to take into account the entire ecosystem of units surrounding them. ④ Many major companies are fundamentally changing their business models by focusing on profitable units and cutting off less profitable ones. ⑤ In order to allow these different units to cooperate successfully, the existence of a common platform is crucial.")
