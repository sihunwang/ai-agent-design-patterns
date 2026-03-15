import asyncio
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

#OPENAI_API_KEY = "API_key_입력"
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# 웹 검색 기능을 포함한 LLM 호출 함수 선언
async def llm_search_async(prompt: str, model: str = "gpt-4.1") -> str:
    response = await async_client.responses.create( #response: newer style
        model = model,
        input = prompt,
        tools = [{"type": "web_search_preview"}], #llm decides if search is needed, call web search, read results, generate answer 
    )
    return response.output_text

# 메인 함수 선언 및 실행
async def main():
    prompt = "오늘의 흥미로운 뉴스를 찾아줘."
    result = await llm_search_async(prompt)
    print("\n💡 웹 검색 결과:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())