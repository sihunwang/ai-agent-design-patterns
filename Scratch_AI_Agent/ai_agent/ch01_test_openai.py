import os
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(
    api_key = OPENAI_API_KEY
)


# client        → API client
# chat          → chat interface
# completions   → response generation endpoint
# create()      → send request to the API


mod = "gpt-4o"
chat_completion = client.chat.completions.create(
    model = mod,
    messages = [
        {
            "role": "user",
            "content": "Say this is a response from " + mod + ".",
        }
    ],
)

# choices → list of generated responses
# message: 모델, 메세지 들 중 메세지
# content → generated text
print(chat_completion.choices[0].message.content)
