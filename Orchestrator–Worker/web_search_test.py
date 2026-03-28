import asyncio
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

#create an instance of OpenAI asynchronus version 
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY) # AsyncOpenAI: asynchronus(비동기) version of the OpenAI Python client 
# 비동기: 사람 1명이 여러 일을 번갈아 처리
# 병렬: 사람 n명이 여러 일을 번갈아 처리

# 웹 검색 기능을 포함한 LLM 호출 함수 선언
async def llm_search_async(prompt: str, model: str = "gpt-4.1") -> str:
    response = await async_client.responses.create( #async_client : 요청을 보내는 주체, response : (최신 버전) 텍스트/이미지/검색 등 상황에 맞는 답 생성 api, create : 실제로 요청을 보내는 메서드
        model = model,
        input = prompt,
        tools = [{"type": "web_search_preview"}], #llm decides if search is needed, call web search, read results, generate answer 
    )
    return response.output_text
# response: 텍스트/이미지/외부 도구 활용 등 상황에 알맞는 답 생성 (신)
# chat.completions: 대화 전용 호출 방식 (구)

# 메인 함수 선언 및 실행
async def main():
    prompt = "오늘의 흥미로운 뉴스를 찾아줘."
    result = await llm_search_async(prompt)
    print("\n💡 웹 검색 결과:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())