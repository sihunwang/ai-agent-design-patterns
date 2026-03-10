import os
from config import OPENAI_API_KEY
from openai import OpenAI       



# OpenAI를 사용하기 위한 클라이언트 객체를 생성합니다. 클라이언트는 사용자를 대신해 LLM에 요청을 보내고 응답을 받아 활용합니다.
client = OpenAI(api_key = OPENAI_API_KEY) 

chat_completion = client.chat.completions.create(
    messages = [    
                    {
                        "role" : "user",
                        "content" : "Say this is a test",
                    }
    ],
    model = "gpt-4o",
)


print(chat_completion.choices[0].message.content)
