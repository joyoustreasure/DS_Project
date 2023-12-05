# print.py

import streamlit as st
from reportlab.lib.pagesizes import letter
import io
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame
from reportlab.lib.units import inch

# 문제를 출력하는 함수
def print_exam():
    # 세션 상태에서 문제들을 가져옵니다.
    questions = st.session_state.get('questions', [])
    
    # 문제들이 있는지 확인하고 출력합니다.
    if questions:
        st.subheader('Generated Questions')
        for i, question_dict in enumerate(questions, start=1):
            # 딕셔너리로부터 문제 텍스트와 선택지 추출
            question_text = question_dict['question']
            options = question_dict['options']
            # 문제를 잘 보이도록 형식을 맞춰서 출력
            st.write(f'Question {i}: {question_text}')
            for option in options:
                st.write(option)
            st.write("")  # 문제 사이에 공백 추가
    else:
        st.write('No questions have been generated yet.')

    add_download_button(questions)

def create_pdf(questions):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()

    # Define custom styles for questions and options
    styles.add(ParagraphStyle(name='QuestionTitle', fontSize=12, spaceAfter=6))
    styles.add(ParagraphStyle(name='QuestionBody', fontSize=10, leading=12))

    # Initialize the list of flowables
    flowables = []

    for i, question_dict in enumerate(questions, start=1):
        question_text = question_dict['question']
        options = question_dict['options']

        # Create a frame for the question and its options
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, showBoundary=1)

        # Add question title and body to the frame
        flowables.append(Paragraph(f'Question {i}:', styles['QuestionTitle']))
        flowables.append(Paragraph(question_text, styles['QuestionBody']))
        for option in options:
            flowables.append(Paragraph(option, styles['QuestionBody']))
        
        # Add a spacer after each question set
        flowables.append(Spacer(1, 0.2 * inch))

    # Build the PDF using the flowables
    doc.build(flowables)
    buffer.seek(0)
    return buffer


def add_download_button(questions):
    if questions:
        pdf_file = create_pdf(questions)
        st.download_button(
            label="Download Questions as PDF",
            data=pdf_file,
            file_name="SAT_questions.pdf",
            mime="application/pdf"
        )
        st.success("I am ready to download the PDF!")

