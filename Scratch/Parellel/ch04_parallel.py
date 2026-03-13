import asyncio
from utils import llm_call_async  # 비동기 방식으로 LLM을 호출하는 함수


# 병렬 처리할 질문 정의
question = (
    "아래 문장을 자연스러운 한국어로 번역해줘.\n"
    "\"Do what you can, with what you have, where you are.\" — Theodore Roosevelt"
)


# 동일한 질문을 여러 LLM 모델에게 동시에 보내기 위한 설정 리스트
parallel_prompt_details = [
    {"user_prompt": question, "model": "gpt-4o"},       # 첫 번째 모델
    {"user_prompt": question, "model": "gpt-4o-mini"},  # 두 번째 모델
    {"user_prompt": question, "model": "o3"},           # 세 번째 모델
]


# 여러 LLM 호출을 병렬로 실행하는 비동기 함수
# async (바로 실행 x, coroutine 생성)
async def run_llm_parallel(prompt_details):

    # 각 LLM 호출을 coroutine 형태의 작업(task) 리스트로 생성 
    # LLM 호출 작업 (아직 실행되지 않은 비동기 작업)
    # model : gpt (실행 예정 비동기 작업 리스트)
    tasks = [
        llm_call_async(prompt['user_prompt'], prompt['model']) # llm aou 호출 1개 비동시
        for prompt in prompt_details
    ]

    responses = []  # (모든)각 모델의 응답을 저장할 리스트

    # 작업이 완료되는 순서대로 결과를 받아 처리
    # 실제 실행
    for task in asyncio.as_completed(tasks): # asyncio: 지금까지 누적 처리된 호출을 동시에 실행
        #tasks에 있는 비동기 작업들을 실행하고 완료되는 순서대로 반환
        #task: Future object -> await 요구

        result = await task  # task가 끝날 때까지 기다리고 결과를 가져와라
        print(result)        # 개별 모델 응답 출력
        responses.append(result)  # 응답 리스트에 저장

    return responses  # 모든 모델 응답 반환


# 메인 비동기 함수
async def main():

    # 여러 LLM을 병렬 호출하여 응답 수집
    responses = await run_llm_parallel(parallel_prompt_details)

    # 여러 모델 응답을 종합하기 위한 최종 프롬프트 생성
    aggregator_prompt = (
        "다음은 사용자의 질문에 대해 여러 LLM이 생성한 응답이야.\n"
        "너의 역할은 이 응답을 종합해 최종 번역문을 제공하는 거야.\n"
        "일부 응답이 부정확하거나 편향될 수 있으니 신뢰성 있고 정확한 답변을 해줘.\n"
        "최종 응답만 출력해.\n\n"
        "사용자 질문:\n"
        f"{question}\n\n"
        "모델 응답:"
    )

    # 각 모델의 응답을 aggregator 프롬프트에 추가
    # responses 배열
    for i in range(len(parallel_prompt_details)):
        aggregator_prompt += f"\n{i+1}. 모델 응답: {responses[i]}\n"

    # 최종 프롬프트 확인용 출력
    print("------------- 최종 프롬프트 -------------\n", aggregator_prompt)

    # aggregator_prompt: 여러 문구 집합

    # 여러 모델의 답변을 종합하여 최종 번역 생성
    final_response = await llm_call_async(aggregator_prompt, model="gpt-4o")

    # 최종 번역 결과 출력
    print("------------- 최종 번역문 -------------\n", final_response)


# 프로그램 실행 진입점
if __name__ == "__main__":

    # asyncio 이벤트 루프 실행 후 main() 비동기 함수 시작
    asyncio.run(main())