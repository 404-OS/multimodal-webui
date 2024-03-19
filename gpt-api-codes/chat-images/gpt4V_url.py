from openai import OpenAI

def chat_with_gpt4V(api_key, prompt, img_url):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"{prompt}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"{img_url}",
                    },
                },
            ],
            }
        ],
        max_tokens=300,
    )
    print(response.choices[0].message.content)

if __name__ == '__main__':
    api_key = "your_api_key_here"
    prompt = "¿Que ves en esta imagen?"
    img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    chat_with_gpt4V(api_key, prompt, img_url)