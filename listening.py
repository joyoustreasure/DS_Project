import streamlit as st
from pathlib import Path
from openai import OpenAI
import os
from pydub import AudioSegment
import random
from mongodb_utils import connect_to_mongodb

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["api_key"])

quiz_collection = connect_to_mongodb("quiz")

def get_script():
    year = random.randint(2015, 2023)
    months = [6, 9, 11]
    month = random.choice(months)    
    number = random.randint(1, 17)
    
    tag = f'{year}_{month:02d}'
    query = { 'tag': tag, 'number': number }

    result = quiz_collection.find_one(query)
    question = result.get('question') 
    script = result.get('script')
    options = result.get('options')
    answer = result.get('answer')
    print(f'tag: {tag}, number: {number}, question: {question}, options: {options}, answer: {answer}, script: {script}')

    return question, script, options, answer

def text_to_speech(dialogue, model="tts-1"):

    for i, sentence in enumerate(dialogue):
        if sentence.startswith('W:'):
            voice = "nova"
            text = sentence[2:]
        elif sentence.startswith('M:'):
            voice = "onyx"
            text = sentence[2:]
        else:
            voice = "nova"
            text = sentence

        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        speech_file_path = Path(st.secrets["audio_dir"]) / f"dialogue_{i}.mp3"
        response.stream_to_file(speech_file_path)

def play_audio_files(audio_folder_path):
    audio_files = [f for f in os.listdir(audio_folder_path) if f.endswith(".mp3")]

    if not audio_files:
        st.warning("No audio files found in the specified directory.")
        return

    audio_segments = [AudioSegment.from_file(os.path.join(audio_folder_path, audio_file)) for audio_file in audio_files]
    combined = sum(audio_segments)
    
    audio_bytes = combined.export(format="mp3").read()
    st.audio(audio_bytes, format="audio/mp3")

    # 생성된 오디오 파일 삭제
    for audio_file in audio_files:
        os.remove(os.path.join(audio_folder_path, audio_file))

def create_listening_questions():
    if 'tts_button_clicked' not in st.session_state:
        st.session_state.tts_button_clicked = False

    tts_button = st.button('Convert Text to Speech')

    if tts_button:
        st.session_state.tts_button_clicked = True
        with st.spinner('Converting text to audio...'):
            st.session_state.question, script, st.session_state.options, st.session_state.answer = get_script()
            text_to_speech(script, model="tts-1")
            play_audio_files(st.secrets["audio_dir"])

    if st.session_state.question:
        st.subheader("Listening Question")
        st.write(st.session_state.question)

        # 선택지에 숫자를 붙여 표시
        if 'options' in st.session_state:
            numbered_options = [f"① {st.session_state.options[0]}", f"② {st.session_state.options[1]}", 
                                f"③ {st.session_state.options[2]}", f"④ {st.session_state.options[3]}", 
                                f"⑤ {st.session_state.options[4]}"]
            option_selected = st.radio("Choose your answer:", numbered_options, key="option_radio")

            if st.button("Check Answer"):
                # 정답 확인
                if option_selected.startswith(st.session_state.answer):
                    st.success("Correct!")
                else:
                    st.error("Incorrect. Try again!")




