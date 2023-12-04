# print.py

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

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