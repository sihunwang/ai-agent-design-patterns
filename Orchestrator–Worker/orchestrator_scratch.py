import asyncio
import json

# utils.py에서 정의된 LLM 호출 함수 import
# llm_call : 일반 LLM 호출 (동기)
# llm_search_async : 웹 검색 도구가 포함된 비동기 LLM 호출
from utils import llm_call, llm_search_async


# ================================
# 오케스트레이터 프롬프트 생성 함수
# ================================
# 사용자 질문을 여러 개의 하위 질문으로 분해하도록
# LLM에게 지시하는 프롬프트를 생성한다.
def get_orchestrator_prompt(user_query):
    return f"""
        다음 사용자 질문을 분석한 뒤, 이를 3개 이내의 관련 하위 질문으로 분해해.
        결과는 JSON 배열로 출력해.
        JSON 배열 안의 각 하위 질문은 다음 형식을 따르는 JSON 객체로 만들어.
        [
            {{
                "question": "하위 질문 1",
                "description": "이 하위 질문의 요지와 의도에 대한 설명"
            }},
            {{
                "question": "하위 질문 2",
                "description": "이 하위 질문의 요지와 의도에 대한 설명"
            }}
        ]

        사용자 질문: {user_query}
        """


# ================================
# 워커 프롬프트 생성 함수
# ================================
# 오케스트레이터가 생성한 하위 질문을 받아
# 각 워커 LLM이 조사 및 분석을 수행하도록 만드는 프롬프트
def get_worker_prompt(user_query, question, description):
    return f"""
            다음 사용자 질문에서 파생된 하위 질문을 보고 응답해.
            사용자 질문: {user_query}
            하위 질문: {question}
            하위 질문의 의도: {description}
            하위 질문을 철저히 분석해 그에 대해 포괄적이고 상세하게 응답해.
            웹 검색 도구를 이용해 자료 조사를 하고, 이를 반영해 응답해.
            """


# ==================================
# 여러 LLM 요청을 병렬로 실행하는 함수
# ==================================
# 여러 워커 LLM 호출을 동시에 실행하기 위해 asyncio를 사용
async def run_llm_parallel(prompt_details):

    # 각 워커 작업을 Task로 생성
    tasks = [
        llm_search_async(item['user_prompt'], item['model'])
        for item in prompt_details
    ]

    # asyncio.gather를 사용해 모든 작업을 병렬 실행
    responses = await asyncio.gather(*tasks)

    return responses


# ==================================
# 오케스트레이터-워커 전체 워크플로 실행 함수
# ==================================
async def run_orchestrator_workflow(user_query):
    # ==================================
    # 1단계 : 오케스트레이터/사용자 질문을 하위 질문으로 분해
    # ==================================
    orchestrator_prompt = get_orchestrator_prompt(user_query) # 하위 질문 생성 프롬프트 양식 + 사용자 질문

    # 오케스트레이터 LLM 호출
    orchestrator_response = llm_call(orchestrator_prompt, model="gpt-4o") # 위에서 생성한 프롬프트를 llm에 넣어 응답 생성 (오케스트레이션 완료)

    # 형식 파싱
    # LLM 응답에 포함된 ```json 코드 블록 제거 후 JSON 파싱
    subtask_list = json.loads(
        orchestrator_response.replace('```json', '').replace('```', '')     # ```json -> 삭제,  ``` -> 삭제
    )

    #     {{
    #     "question": "하위 질문 2",
    #     "description": "이 하위 질문의 요지와 의도에 대한 설명"
    # }}

    # 사용자를 위한 생성된 하위 질문 출력
    for i, subtask in enumerate(subtask_list, start=1):
        print(f"\n--- 하위 질문 {i} ---")
        print("질문:", subtask['question']) # 하위 질문
        print("설명:", subtask['description']) # 하위 질문 의도

    # ==================================
    # 2단계 : 각 하위 질문을 처리할 워커 프롬프트 생성
    # ==================================
        
    # worker_prompt_details = [
    # {
    #     "user_prompt": "프롬프트 문자열 1",
    #     "model": "gpt-4.1"
    # },
    # {
    #     "user_prompt": "프롬프트 문자열 1",
    #     "model": "gpt-4.1"
    # },

    worker_prompt_details = [
        {
            "user_prompt": get_worker_prompt(
                user_query,
                subtask["question"],
                subtask["description"]
            ),
            "model": "gpt-4.1"
        }
        for subtask in subtask_list
    ]
    # subtask_list: 딕셔너리 리스트
    # subtask: 딕셔너리

    # # 첫 번째 워커 프롬프트 확인 (디버깅용)
    # print("\n=========== 샘플 워커 프롬프트 ===========")
    # print(worker_prompt_details[0]['user_prompt'])

    # ==================================
    # 3단계 : 워커 LLM 병렬 실행
    # ==================================
    worker_responses = await run_llm_parallel(worker_prompt_details)

    print("\n=========== 워커 응답 결과 ===========")
    for i, response in enumerate(worker_responses, 1):
        print(f"\n--- 하위 질문 {i} 응답 ---")
        print(response)

    # ==================================
    # 4단계 : 애그리게이터 프롬프트 생성
    # ==================================
    # 여러 워커의 응답을 종합하여
    # 하나의 최종 답변을 생성하도록 LLM에 요청
    aggregator_prompt = (
        "다음은 사용자 질문을 하위 질문으로 나누고 받은 응답이야.\n"
        "이 내용을 모두 종합해 최종 답변을 해.\n"
        "하위 질문의 응답을 최대한 포괄적이고 상세하게 포함해.\n"
        f"사용자 질문: {user_query}\n\n"
        "하위 질문 및 응답:\n"
    )

    # 각 워커 결과를 애그리게이터 프롬프트에 추가
    for i, subtask in enumerate(subtask_list):
        aggregator_prompt += f"\n{i+1}. 하위 질문: {subtask['question']}\n"
        aggregator_prompt += f" 응답: {worker_responses[i]}\n"

    # 애그리게이터 프롬프트 출력 (디버깅용)
    print("\n====== 애그리게이터 프롬프트 ======\n", aggregator_prompt)

    # ==================================
    # 5단계 : 최종 보고서 생성
    # ==================================
    final_response = llm_call(aggregator_prompt, model="gpt-4.1")

    print("\n=========== 최종 보고서 결과 ===========")
    print(final_response)


# ==================================
# 프로그램 실행 시작점
# ==================================
async def main():

    # 사용자 질문 입력
    user_query = "2025년, AI 서비스는 어떻게 발전했을까?"

    # 전체 워크플로 실행
    final_output = await run_orchestrator_workflow(user_query)


# Python 파일을 직접 실행했을 때 main 실행
if __name__ == "__main__":
    asyncio.run(main())