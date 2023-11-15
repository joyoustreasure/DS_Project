import streamlit as st

# 여기에 FAQ 데이터를 정의합니다.
faq_data = {
    "What is GPT Lab?": "GPT Lab is a user-friendly app that allows anyone to interact with and create their own AI Assistants powered by OpenAI's GPT language model. With GPT Lab, you can interact with pre-built AI Assistants or create your own by specifying a prompt and OpenAI model parameters. Our goal is to make AI accessible and easy to use for everyone, so you can focus on designing your Assistant without worrying about the underlying infrastructure.",
    "Why use GPT Lab instead of Chat GPT?": "GPT Lab aims to be the GitLab for your favorite prompts, allowing you to save and reuse your favorite prompts as AI Assistants. This eliminates the need to retype the same prompt every time you want to use it. Additionally, you can share your AI Assistants with others without revealing your exact prompt. Since you're using your own OpenAI API key, you don't have to worry about Chat GPT being at capacity.",
    "What is an OpenAI API Key and why do I need one?": "An OpenAI API key is a unique credential that allows you to interact with OpeAI's GPT models. It also serves as your identifier in GPT Lab, allowing us to remember the AI Assistants you have created.",
}

def create_faq_section():
    st.header('General Question')
    for question, answer in faq_data.items():
        with st.expander(question):
            st.write(answer)
