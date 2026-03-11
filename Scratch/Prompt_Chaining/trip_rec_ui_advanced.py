import streamlit as st
from typing import List
from utils import llm_call

default_prompts = [
"""사용자의 여행 취향을 바탕으로 적합한 여행지 세 곳을 추천해.
- 사용자가 입력한 내용을 요약해.
- 추천한 여행지가 왜 적합한지 설명해.
- 각 여행지의 기후, 주요 관광지를 알려줘.
- 여행지 이름을 명확히 세 개 제시해.""",

"""사용자가 선택한 여행지를 바탕으로 해당 여행지에서 할 수 있는 활동을 제안해.
- 왜 이 여행지가 적합한지 설명해.
- 자연 탐방, 역사 탐방, 음식 체험 등 다양한 활동 다섯 가지를 제안해.""",

"""선택된 여행지의 하루 여행 일정을 만들어줘.
- 오전, 오후, 저녁으로 나눠 설명해.
- 각 시간대에 어떤 활동을 하면 좋은지 설명해."""
]

def llm_step(prompt: str, initial_input: str, previous_response: str):
    final_prompt = f"""{prompt}

처음에 사용자가 입력한 내용은 다음과 같아.
{initial_input}

또한 응답 시 아래 내용도 참고해.
{previous_response}
"""
    response = llm_call(final_prompt)
    return response, final_prompt


def main():

    st.set_page_config(page_title="프롬프트 체이닝 에이전트", layout="wide")

    st.title("프롬프트 체이닝 여행 에이전트")

    initial_input = st.text_area(
        "여행 스타일 입력",
        value="따뜻한 날씨를 좋아하고 자연 경관과 역사적인 장소를 둘러보는 걸 선호해."
    )

    if "step" not in st.session_state:
        st.session_state.step = 0

    if "previous_response" not in st.session_state:
        st.session_state.previous_response = initial_input

    if "responses" not in st.session_state:
        st.session_state.responses = []

    if "prompts" not in st.session_state:
        st.session_state.prompts = []

    st.divider()

    # Step 1 : 여행지 추천
    if st.session_state.step == 0:

        if st.button("여행지 추천 받기"):

            response, final_prompt = llm_step(
                default_prompts[0],
                initial_input,
                st.session_state.previous_response
            )

            st.session_state.responses.append(response)
            st.session_state.prompts.append(final_prompt)

            st.session_state.previous_response = response
            st.session_state.step = 1

    if st.session_state.step >= 1:

        st.subheader("추천 여행지")

        st.write(st.session_state.responses[0])

        st.divider()

        # 사용자 선택
        selected_place = st.text_input("위 여행지 중 하나를 입력하세요")

        if st.button("선택한 여행지로 활동 추천") and selected_place:

            st.session_state.previous_response = selected_place

            response, final_prompt = llm_step(
                default_prompts[1],
                initial_input,
                selected_place
            )

            st.session_state.responses.append(response)
            st.session_state.prompts.append(final_prompt)

            st.session_state.previous_response = response
            st.session_state.step = 2

    # Step 2 : 활동 추천
    if st.session_state.step >= 2:

        st.subheader("추천 활동")

        st.write(st.session_state.responses[1])

        if st.button("하루 일정 생성"):

            response, final_prompt = llm_step(
                default_prompts[2],
                initial_input,
                st.session_state.previous_response
            )

            st.session_state.responses.append(response)
            st.session_state.prompts.append(final_prompt)

            st.session_state.previous_response = response
            st.session_state.step = 3

    # Step 3 : 일정 생성
    if st.session_state.step >= 3:

        st.subheader("최종 여행 일정")

        st.write(st.session_state.responses[2])

    st.divider()

    # 디버깅용 단계 확인
    with st.expander("프롬프트와 응답 보기"):

        for i in range(len(st.session_state.responses)):

            st.markdown(f"### {i+1} 단계 프롬프트")

            st.code(st.session_state.prompts[i])

            st.markdown("응답")

            st.write(st.session_state.responses[i])


if __name__ == "__main__":
    main()