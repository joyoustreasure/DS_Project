# print.py

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import ast

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

    # PDF 생성 함수
    def create_pdf(questions):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        flowables = []
        
        for i, question_dict in enumerate(questions, start=1):
            question_text = question_dict['question']
            options = question_dict['options']
            
            # 문제와 선택지를 PDF에 추가
            flowables.append(Paragraph(f'Question {i}: {question_text}', styles['Heading2']))
            for option in options:
                flowables.append(Paragraph(option, styles['Normal']))
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