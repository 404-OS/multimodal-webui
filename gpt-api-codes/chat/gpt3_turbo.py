import os
import sys
import requests
from openai import OpenAI

# Aquí puedes procesar img_str, que es tu imagen en base64
def chat_with_gpt35(api_key, system_prompt, user_prompt):
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"{system_prompt}"
            },
            {
                "role": "user",
                "content": f"{user_prompt}"
            }
        ]
    )
    print(response.choices[0].message.content)

if __name__ == '__main__':
    api_key = "your_api_key_here"
    system_prompt = "De ahora en adelante actua como un experto comercial en la captacion de potenciales clientes"
    user_prompt = "¿Que puedes decirme de la empresa Impelia Formacion Profesional?"
    chat_with_gpt35(api_key, system_prompt, user_prompt)