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
    # TTS 변환 버튼
    tts_button = st.button('Convert Text to Speech')

    # TTS 변환 수행
    if tts_button:
        with st.spinner('Converting text to audio...'):
            question, script, options, answer = get_script()
            # 여기서 `model` 매개변수를 명시적으로 전달
            text_to_speech(script, model="tts-1")
            play_audio_files(st.secrets["audio_dir"])