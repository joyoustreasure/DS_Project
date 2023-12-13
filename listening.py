import streamlit as st
from pathlib import Path
from openai import OpenAI

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["api_key"])

def text_to_speech(text, model="tts-1", voice="alloy"):
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text
    )

    # Streamlit의 임시 디렉토리에 오디오 파일 저장 및 파일 경로 반환
    speech_file_path = Path(st.secrets["temp_dir"]) / "speech.mp3"
    response.stream_to_file(speech_file_path)
    return speech_file_path.as_posix()

def create_listening_questions():
    # 음성 선택 옵션
    voice_options = ['nova', 'shimmer', 'echo', 'onyx', 'fable', 'alloy']
    selected_voice = st.selectbox('Choose a voice:', voice_options)

    # 사용자로부터 텍스트 입력 받기
    user_input = st.text_area("Enter text for TTS conversion:")

    # TTS 변환 버튼
    tts_button = st.button('Convert Text to Speech')

    # TTS 변환 수행
    if tts_button and user_input:
        with st.spinner('Converting text to audio...'):
            # 여기서 `model` 매개변수를 명시적으로 전달
            audio_data = text_to_speech(user_input, model="tts-1", voice=selected_voice)
            st.audio(audio_data) 