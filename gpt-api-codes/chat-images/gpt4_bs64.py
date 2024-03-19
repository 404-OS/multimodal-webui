import base64
from openai import OpenAI

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def chat_with_gpt4V(api_key, prompt, base64_image):
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
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ],
            }
        ],
        max_tokens=300,
    )
    print(response.choices[0].message.content)

if __name__ == '__main__':
    api_key = "your_api_key_here"
    prompt = "¿Que ves en esta imagen?"
    image_path = "playa.jpg"
    base64_image = encode_image(image_path)
    chat_with_gpt4V(api_key, prompt, base64_image)