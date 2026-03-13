import os
from openai import OpenAI
from Scratch_AI_Agent.Prompt_Chaining.config import OPENAI_API_KEY

client = OpenAI(
    api_key = OPENAI_API_KEY
)


# client        → API client
# chat          → chat interface
# completions   → response generation endpoint (응답을 생성하는 API 호출 지점) - 기능 선택
# create()      → send request to the API - 실제 요청


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
print(chat_completion.choices[0].message.content) #"Say this is a response from " + mod + ".", 관련 답변
