import streamlit as st
import openai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

def question():
    # OpenAI API 키를 설정합니다.
    openai.api_key = st.secrets["api_key"]

    # 스트림릿의 페이지 설정을 정의합니다: 페이지의 타이틀과 아이콘을 설정합니다.
    # st.set_page_config(
    #     page_title="SAT 영어 문제 생성기",
    #     page_icon="📘"
    # )

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

    if st.button('Fill-in-the-Blank Inference'):
        prompt_type = "Create a fill-in-the-blank question that tests inference skills."
        # 프롬프트 생성 및 문제 생성 코드

    if st.button('Sequence Shuffling'):
        prompt_type = "Create a sequence shuffling question where paragraphs are out of order."
        # 프롬프트 생성 및 문제 생성 코드

    if st.button('Title Matching'):
        prompt_type = "Create a title matching question where students match titles to paragraphs."
        # 프롬프트 생성 및 문제 생성 코드

    if st.button('Correct Sentence Insertion'):
        prompt_type = "Create a question where students must insert a sentence into a passage."
        # 프롬프트 생성 및 문제 생성 코드

    if st.button('Word Meaning Comprehension'):
        prompt_type = "Create a question testing the comprehension of the meaning of a word in context."
        # 프롬프트 생성 및 문제 생성 코드

    MAX_COMPLETION_TOKENS = 4096 - 342 

    # 각 문제 유형에 대한 프롬프트와 문제 생성을 처리하는 공통 코드를 정의합니다.
    def generate_question():
        gpt_prompt = "너는 수능 영어 출제위원이야." \
                  "A fascinating species of water flea exhibits a kind of flexibility that evolutionary biologists call adaptive plasticity. " \
                  "(A) That’s a clever trick, because producing spines and a helmet is costly, in terms of energy, and conserving energy is essential for an organism’s ability to survive and reproduce. The water flea only expends the energy needed to produce spines and a helmet when it needs to. " \
                  "(B) If the baby water flea is developing into an adult in water that includes the chemical signatures of creatures that prey on water fleas, it develops a helmet and spines to defend itself against predators. If the water around it doesn’t include the chemical signatures of predators, the water flea doesn’t develop these protective devices. " \
                  "(C) So it may well be that this plasticity is an adaptation: a trait that came to exist in a species because it contributed to reproductive fitness. There are many cases, across many species, of adaptive plasticity. Plasticity is conducive to fitness if there is sufficient variation in the environment. " \
                  "위와 유사한 형식으로 경제 주제로 맞게 5지선다 문제 내고 답도 제시해줘." \
    
        with st.spinner("Generating question..."):
            gpt_response = openai.Completion.create(
                model="text-davinci-003",
                prompt=gpt_prompt,
                max_tokens = MAX_COMPLETION_TOKENS
            )
        return gpt_response.choices[0].text

    # # 버튼이 눌린 경우에 해당하는 프롬프트를 생성하고 문제를 생성합니다.
    # if 'prompt_type' in locals():
    #     question = generate_question()
    #     generated_text = question
    #     approx_chars_per_line = 80
    #     lines = len(generated_text) / approx_chars_per_line
    #     height = max(300, int(lines * 1.5))
    #     st.text_area("Generated Question", question, height=height)
        
    #     if 'questions' not in st.session_state:
    #         st.session_state['questions'] = []  # 처음으로 문제를 저장할 때 리스트를 초기화합니다.
    #     st.session_state['questions'].append(question)
    #     st.image("hard.gif")
    # 문제 생성
    if 'prompt_type' in locals():
        question = generate_question()
        generated_text = question
        approx_chars_per_line = 80
        lines = len(generated_text) / approx_chars_per_line
        height = max(300, int(lines * 1.5))
        st.text_area("Generated Question", question, height=height)

        # 저장하기 버튼
        if st.button('Save Question'):
            if 'questions' not in st.session_state:
                st.session_state['questions'] = []  # 처음으로 문제를 저장할 때 리스트를 초기화합니다.
            st.session_state['questions'].append(question)
            st.success("Question saved successfully!")  # 저장 완료 메시지

        st.image("hard.gif")
        
# 문제를 출력하는 함수
def print_exam():
    # 세션 상태에서 문제들을 가져옵니다.
    questions = st.session_state.get('questions', [])
    
    # 문제들이 있는지 확인하고 출력합니다.
    if questions:
        st.subheader('Generated Questions')
        for i, question in enumerate(questions, start=1):
            st.write(f'Question {i}:')
            st.text_area(f'Question {i} Text', question, height=300, key=f'Question{i}')
    else:
        st.write('No questions have been generated yet.')

    # PDF 생성 함수
    def create_pdf(questions):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        flowables = []
        
        for i, question in enumerate(questions, start=1):
            flowables.append(Paragraph(f'Question {i}:', styles['Heading2']))
            flowables.append(Paragraph(question, styles['Normal']))
            flowables.append(Spacer(1, 12))
        
        doc.build(flowables)
        buffer.seek(0)
        return buffer

    # PDF 다운로드 버튼을 추가하는 함수
    def add_download_button(questions):
        if questions:
            pdf_file = create_pdf(questions)
            st.download_button(
                label="Download Questions as PDF",
                data=pdf_file,
                file_name="SAT_questions.pdf",
                mime="application/pdf"
            )
            st.success("Success, PDF download!")

    # 스트림릿 앱에서 문제 목록을 가져오는 코드
    questions = st.session_state.get('questions', [])

    # PDF 다운로드 버튼을 추가합니다.
    add_download_button(questions)
    