import asyncio
import json
from utils import llm_call, llm_search_async


def get_orchestrator_prompt(user_query):
    return f"""
    다음 사용자 질문을 필요한 만큼의 하위 질문으로 분해하고 JSON 배열로 출력해.

    사용자 질문: {user_query}
    """


def get_worker_prompt(user_query, question, description):
    return f"""
    사용자 질문: {user_query}
    하위 질문: {question}
    의도: {description}

    웹 검색 필요시에 적용하여 분석해.
    """


async def run_orchestrator_workflow(user_query):

    # 1 질문 분해
    response = llm_call(get_orchestrator_prompt(user_query), model="gpt-4o")

    subtask_list = json.loads(response.replace("```json", "").replace("```", ""))

    print("\n=== 생성된 하위 질문 ===")

    for i, s in enumerate(subtask_list, 1):
        print(i, s["question"])

    # 2 병렬 조사
    tasks = [
        llm_search_async(
            get_worker_prompt(user_query, s["question"], s["description"]), "gpt-4.1"
        )
        for s in subtask_list
    ]

    worker_responses = await asyncio.gather(*tasks)

    # 3 결과 통합
    aggregator_prompt = f"""
    다음 정보를 종합해 최종 답변을 작성해.

    사용자 질문: {user_query}

    """

    for s, r in zip(subtask_list, worker_responses):
        aggregator_prompt += f"\n질문: {s['question']}\n답변: {r}\n"

    final = llm_call(aggregator_prompt, model="gpt-4.1")

    print("\n=== 최종 결과 ===")
    print(final)


async def main():
    await run_orchestrator_workflow("2025년 AI 서비스는 어떻게 발전했을까?")


if __name__ == "__main__":
    asyncio.run(main())
