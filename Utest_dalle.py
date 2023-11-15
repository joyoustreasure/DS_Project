import streamlit as st  # streamlit 라이브러리를 st라는 이름으로 가져옵니다.
import openai  # openai 라이브러리를 가져옵니다.

openai.api_key = st.secrets["api_key"]  # Streamlit의 시크릿 기능을 사용하여 OpenAI API 키를 설정합니다.

st.title("ChatGPT Plus DALL-E")  # 웹 페이지에 "ChatGPT Plus DALL-E"라는 제목을 설정합니다.

with st.form("form"):  # 'form'이라는 이름의 Streamlit 폼을 생성합니다.
    user_input = st.text_input("Prompt")  # 사용자로부터 텍스트 입력을 받습니다. "Prompt"는 입력 필드의 레이블입니다.
    size = st.selectbox("Size", ["1024x1024", "512x512", "256x256"])  # 드롭다운 상자를 통해 이미지 크기를 선택할 수 있습니다.
    submit = st.form_submit_button("Submit")  # 폼 제출 버튼을 만듭니다.

if submit and user_input:  # 사용자가 'Submit' 버튼을 클릭하고 입력을 했을 경우에 실행됩니다.
    gpt_prompt = [{  # ChatGPT에 전달할 프롬프트 구조를 생성합니다.
        "role": "system",  # 시스템의 역할을 나타냅니다.
        "content": "Imagine the detail appearance of the input. Response it shortly around 20 words"  # 시스템에게 입력의 상세한 모습을 상상하고 20단어 내로 응답하라는 지시를 합니다.
    }]

    gpt_prompt.append({  # 사용자의 입력을 추가합니다.
        "role": "user",  # 사용자의 역할을 나타냅니다.
        "content": user_input  # 사용자 입력을 내용으로 합니다.
    })

    with st.spinner("Waiting for ChatGPT..."):  # ChatGPT의 응답을 기다리는 동안 스피너(로딩 아이콘)를 표시합니다.
        gpt_response = openai.ChatCompletion.create(  # ChatGPT 모델을 사용하여 응답을 생성합니다.
            model="gpt-3.5-turbo",  # 사용할 모델을 지정합니다.
            messages=gpt_prompt  # 위에서 생성한 프롬프트를 전달합니다.
        )

    prompt = gpt_response["choices"][0]["message"]["content"]  # ChatGPT의 응답을 prompt 변수에 저장합니다.
    st.write(prompt)  # 응답을 웹 페이지에 표시합니다.

    with st.spinner("Waiting for DALL-E..."):  # DALL-E의 응답을 기다리는 동안 스피너를 표시합니다.
        dalle_response = openai.Image.create(  # DALL-E 모델을 사용하여 이미지를 생성합니다.
            prompt=prompt,  # ChatGPT로부터 받은 프롬프트를 사용합니다.
            size=size  # 사용자가 선택한 이미지 크기를 사용합니다.
        )

    st.image(dalle_response["data"][0]["url"])  # 생성된 이미지를 웹 페이지에 표시합니다.
