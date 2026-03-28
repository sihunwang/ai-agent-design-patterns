import streamlit as st          
import asyncio                  # 비동기 처리를 위한 파이썬 기본 라이브러리
from utils import llm_call_async  # 비동기 방식으로 LLM을 호출하는 함수


# 여러 LLM을 동시에 호출하는 병렬 실행 함수
async def run_llm_parallel(prompt_details):

    # 여러 모델 호출을 위한 작업(task) 리스트 생성
    # prompt_details 안에는 {"user_prompt": 질문, "model": 모델} 형태의 dict가 들어있다
    tasks = [
        llm_call_async(prompt["user_prompt"], prompt["model"])
        for prompt in prompt_details
    ]

    responses = []   # 각 모델의 응답을 저장할 리스트


    # asyncio.as_completed()
    # → 여러 작업이 완료되는 순서대로 결과를 받아오는 방식
    for task in asyncio.as_completed(tasks):
        result = await task     # 작업이 끝날 때까지 기다린 후 결과 받기
        responses.append(result)


    # Streamlit expander
    # → 클릭하면 펼쳐지는 UI 영역
    # 모든 모델 응답을 접어두었다가 볼 수 있게 만든다
    with st.expander("모델 응답 전체 보기"):
        for response in responses:
            st.markdown(f" 모델 응답: {response}")


    return responses   # 모든 모델 응답 리스트 반환



# 병렬 에이전트 실행 함수
async def run_parallel_agent(question, selected_models):

    # 각 모델에 보낼 프롬프트 구성
    # 예:
    # {"user_prompt": question, "model": "gpt-4o"}
    parallel_prompt_details = [
        {"user_prompt": question, "model": model} for model in selected_models
    ]


    # 여러 모델을 동시에 호출
    responses = await run_llm_parallel(parallel_prompt_details)


    # 여러 모델의 응답을 종합하기 위한 Aggregator 프롬프트 생성
    aggregator_prompt = (
        "다음은 여러 LLM이 사용자의 질문에 대해 생성한 응답이야.\n"
        "너의 역할은 이 응답을 모두 종합해 최종 번역문을 제공하는 거야.\n"
        "일부 응답이 부정확하거나 편향될 수 있으니 신뢰성 있고 정확한 답변을 해줘.\n"
        "최종 응답만 출력해.\n"
        "사용자 질문:\n"
        f"{question}\n\n"
        "모델 응답:"
    )


    # 각 모델의 응답을 Aggregator 프롬프트에 추가
    for i in range(len(parallel_prompt_details)):
        aggregator_prompt += f"\n{i+1}. 모델 응답: {responses[i]}\n"


    # Streamlit expander
    # 실제 LLM에게 전달되는 최종 프롬프트를 확인할 수 있게 만든 UI
    with st.expander("최종 프롬프트 보기", expanded=False):
        st.code(aggregator_prompt, language='markdown')


    # Aggregator 모델 호출
    # 여러 모델의 응답을 종합해 최종 답변 생성
    final_response = await llm_call_async(aggregator_prompt, model="gpt-4o")


    # Streamlit UI에 최종 결과 출력
    st.subheader("최종 응답")
    st.markdown(final_response)



# Streamlit 앱의 메인 함수
def main():

    # 웹 페이지 상단 제목
    st.title("병렬 처리 에이전트")


    # 사용자 질문 입력 영역
    # text_area는 여러 줄 입력 가능한 UI
    question = st.text_area(
        "✍ 사용자 질문",
        height = 100,
        value = """아래 문장을 자연스러운 한국어로 번역해줘.
"Do what you can, with what you have, where you are." — Theodore Roosevelt
"""
    )


    # 사용 가능한 모델 리스트
    model_options = ["gpt-4o", "gpt-4o-mini", "o3"]


    # Streamlit multiselect
    # 여러 모델을 선택할 수 있는 UI
    selected_models = st.multiselect(
        "🔍 사용할 모델을 선택하세요.",
        model_options,
        default = model_options[:3]   # 기본값: 모든 모델 선택
    )


# 에이전트 실행 버튼
    if st.button("에이전트 실행"):

        # 질문이 비어있는 경우
        if not question.strip():
            st.warning("❗ 질문을 입력하세요.")

        # 모델이 선택되지 않은 경우
        elif not selected_models:
            st.warning("❗ 한 가지 이상의 모델을 선택하세요.")

        else:
            # 비동기 함수 실행
            asyncio.run(run_parallel_agent(question.strip(), selected_models))



# 파이썬 스크립트 직접 실행 시 main() 호출
if __name__ == "__main__":
    main()