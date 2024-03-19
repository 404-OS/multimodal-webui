import os
import sys
import requests
from openai import OpenAI

# Aquí puedes procesar img_str, que es tu imagen en base64
def chat_with_gpt4(api_key, audio_file_path):
    client = OpenAI(api_key=api_key)

    audio_file= open(audio_file_path, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file, 
        response_format="text"
    )
    print(transcript)

if __name__ == '__main__':
    api_key = "your_api_key_here"
    audio_file_path = ""
    chat_with_gpt4(api_key, audio_file_path)