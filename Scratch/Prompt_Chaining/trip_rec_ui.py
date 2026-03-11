import streamlit as st
from typing import List
from utils import llm_call

default_prompts = [
    """사용자의 여행 취향을 바탕으로 적합한 여행지 세 곳을 추천해.
    - 사용자가 입력한 내용을 요약해.
    - 추천한 여행지가 왜 적합한지 설명해.
    - 각 여행지의 기후, 주요 관광지를 알려줘.""",
    """가장 추천하는 여행지 한 곳을 선정하고, 거기서 할 수 있는 활동을 제안해.
    - 왜 최종 여행지로 선정했는지 설명해.
    - 해당 여행지에서 즐길 수 있는 다섯 가지 활동을 나열해.
    - 자연 탐방, 역사 탐방, 음식 체험 등 다양한 영역의 활동을 골라줘.""",
    """추천한 여행지의 하루 일정 계획을 세워줘.
    - 오전, 오후, 저녁으로 나눠 일정을 짜줘.
    - 각 시간대에 어떤 활동을 하면 좋을지 설명해.""",
]


# 프롬프트 체이닝 함수 개선
def prompt_chain_workflow(initial_input: str, prompt_chain: List[str]) -> List[str]:
    # 이전 단계의 LLM 응답 저장
    # 다음 프롬프트에서 참고할 컨텍스트로 사용
    previous_response = initial_input  # 대답 - return 예정

    # 각 단계의 LLM 응답을 저장하는 리스트
    response_chain = []  # 대답 모음

    # 실제 LLM에게 전달된 최종 프롬프트 저장 (디버깅용) - 사용자가 확인, 수정을 함
    final_prompts = []  # prompt 모음 (대답 포함한) - return 예정

    for i, prompt in enumerate(prompt_chain, 1):

        if i == 1:
            final_prompt = f"""{prompt}

            처음에 사용자가 입력한 내용은 다음과 같아. 응답할 때 항상 이 내용을 고려해.
                {initial_input}"""
        else:
            final_prompt = f"""{prompt}

            처음에 사용자가 입력한 내용은 다음과 같아. 응답할 때 항상 이 내용을 고려해.
                {initial_input}

                또한 응답 시 아래 내용도 참고해.
                {previous_response}"""

        # 실제 LLM에 전달된 프롬프트 저장
        final_prompts.append(final_prompt)
        # LLM 호출
        response = llm_call(final_prompt)
        # 응답 저장
        response_chain.append(response)
        # 다음 단계에서 참고하도록 업데이트
        previous_response = response

    return response_chain, final_prompts


# 메인 함수 선언 및 페이지 설정
def main():
    # 웹페이지 기본 설정
    st.set_page_config(
        page_title="프롬프트 체이닝 에이전트", layout="wide"
    )  # 브라우저 탭 제목

    # 페이지 제목
    st.title("프롬프트 체이닝 에이전트(여행 일정 수립)")

    # 텍스트 입력창 생성
    initial_input = st.text_area(
        "여행 스타일 입력",
    )

    # 단계별 프롬프트 설정창 생성
    # 단계별 프롬프트 수정 UI
    custom_prompts = []

    # expander: 접었다 펼칠 수 있는 UI
    with st.expander("⚙ 단계별 프롬프트 설정", expanded=False):
        for i, default_prompt in enumerate(default_prompts, 1):
            edited = st.text_area(
                f"프롬프트 {i}", value=default_prompt, height=140, key=f"prompt_{i}"
            )
            # 사용자가 수정한 프롬프트 저장
            custom_prompts.append(edited)

    # 프롬프트 체인 실행
    # 실행 버튼
    if st.button("🚀 프롬프트 체인 실행"):
        # 결과 탭 생성
        final_result_tab, details_tab = st.tabs(["✨ 최종 결과", "🔄 세부 단계"])
        # 실행 중 표시
        with st.spinner("실행 중입니다..."):
            results, final_prompts = prompt_chain_workflow(
                initial_input, custom_prompts
            )
        # 최종 결과 탭
        with final_result_tab:
            st.write(results[-1])
        # 세부 단계 탭
        with details_tab:
            for i in range(len(custom_prompts)):
                with st.expander(f"📝 {i+1} 단계: 프롬프트와 응답", expanded=False):
                    st.markdown(f"===== 프롬프트 =====")
                    st.code(final_prompts[i])
                    st.markdown(f"===== 응답 =====")
                    st.write(results[i])


# Streamlit 실행 진입점
# streamlit run main.py 실행 시 main() 호출됨
if __name__ == "__main__":
    main()
