import streamlit as st
import openai

# OpenAI API 키를 설정합니다.
# 이 키는 환경변수로부터 가져오거나, 보안이 유지되는 방식으로 관리해야 합니다.
openai.api_key = 'your-api-key'

# Streamlit 애플리케이션의 타이틀 설정
st.title('영어 문제 생성기')

# 문제 유형 선택
question_type = st.radio(
    "문제 유형을 선택하세요:",
    ('문법 오류 찾기', '단어로 문장 완성하기', '문단 요약하기')
)

# 사용자 입력 받기
if question_type == '문법 오류 찾기':
    input_text = st.text_area("문장을 입력하세요:")
    prompt_text = f"다음 문장에는 문법적인 오류가 하나 포함되어 있습니다. 오류를 찾아 정정하십시오: '{input_text}'"
elif question_type == '단어로 문장 완성하기':
    input_word = st.text_input("단어를 입력하세요:")
    prompt_text = f"다음 단어를 사용하여 문장을 완성하십시오: '{input_word}'"
elif question_type == '문단 요약하기':
    paragraph = st.text_area("문단을 입력하세요:")
    prompt_text = f"다음 단락을 읽고 주요 내용을 요약하는 질문에 답하세요: '{paragraph}'"

# 문제 생성 버튼
if st.button('문제 생성'):
    # OpenAI API 호출하여 결과를 가져옵니다.
    response = openai.Completion.create(
        engine="text-davinci-003",  # 또는 다른 GPT-3/GPT-4 모델을 사용하세요.
        prompt=prompt_text,
        max_tokens=150
    )

    # API로부터 받은 응답을 표시합니다.
    st.subheader('생성된 문제:')
    st.write(response.choices[0].text.strip())

# 스트림릿 애플리케이션을 실행하려면 스크립트를 저장하고, 콘솔에서 `streamlit run your_script.py` 명령을 사용합니다.
