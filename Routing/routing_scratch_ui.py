import streamlit as st
import re
from utils import llm_call


# LLM을 이용해 사용자 질문의 유형을 분류하는 함수
def llm_router_call(user_prompt: str) -> str:
    router_prompt = f"""
    사용자 질문: {user_prompt}

    위 질문에 대해 가장 적절한 유형을 하나 골라:
    - 일상: 일반적인 대화, 일정 짜기, 정보 요청 등
    - 빠른: 계산, 단답형 질문, 간단한 명령 등
    - 코딩: 파이썬, 코드 작성, 오류 디버깅 등
    단답형으로 유형만 출력해.
    """
    # 경량 모델로 사용자 질문이 어떠한 유형인지 선정한다.
    routing_result = llm_call(router_prompt, model="gpt-4o-mini").strip()
    return routing_result


# 경로별 함수 선언
# 일상 에이전트
def run_general_agent(user_prompt: str):
    prompt = f"""
    너는 다재다능한 일상 도우미야.
    여행 일정, 추천, 요약 등 일상적인 질문에 친절하고 유용하게 답변하지.

    [사용자 질문]
    {user_prompt}
    """
    response = llm_call(prompt, model="gpt-4o")  # 노멀
    st.write("### 📘 일상 에이전트 응답")
    st.write(response)


# 빠른 에이전트
def run_quick_agent(user_prompt: str):
    prompt = f"""
    너는 빠르고 간단한 응답을 제공하는 빠른 에이전트야.
    사용자의 질문에 두괄식으로 간결하게 답변하지.

    [사용자 질문]
    {user_prompt}
    """
    response = llm_call(prompt, model="gpt-4o-mini")  # 경량
    st.markdown("### ⚡ 빠른 에이전트 응답")
    st.success(response)


# 코딩 에이전트
def run_coding_agent(user_prompt: str):
    prompt = f"""
    너는 뛰어난 코딩 비서야.
    파이썬, 자바스크립트, API 개발, 오류 디버깅 등에 능숙해.
    질문에 대해 최대한 정확하고 실행 가능한 코드를 제공해.
    답변할 때 항상 완결성 있는 코드를 출력하면서 마무리하지.

    [사용자 질문]
    {user_prompt}
    """
    response = llm_call(prompt, model="o3")  # 추론

    # 마지막 코드 블록 추출
    # --------------------------------
    # LLM 응답에서 코드 블록만 추출
    # --------------------------------
    # ```python ... ``` 형식의 코드 블록을 찾음
    code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", response, re.DOTALL)
    # 마지막 코드 블록을 최종 코드로 사용
    last_code = code_blocks[-1].strip() if code_blocks else None

    # Streamlit 화면에 제목 출력
    st.markdown("### 📘 코딩 에이전트 응답")

    # Streamlit 탭 UI 생성
    # 첫번째 탭: 전체 LLM 응답
    # 두번째 탭: 최종 코드만 표시
    tab1, tab2 = st.tabs(["📝 전체 응답", "💻 최종 코드"])

    # 첫번째 탭 내용
    with tab1:
        st.write(response)

    # 두번째 탭 내용
    with tab2:
        if last_code:
            # 코드 블록 스타일로 출력
            st.code(last_code, language="python")
        else:
            # 코드가 없으면 안내 메시지 출력
            st.info("코드 블록이 감지되지 않았습니다.")


# --------------------------------
# Streamlit 앱 시작 지점
# --------------------------------
if __name__ == "__main__":

    # Streamlit 웹페이지 기본 설정
    # page_title → 브라우저 탭 제목
    # layout → 화면 레이아웃 (centered / wide)
    st.set_page_config(page_title="라우팅 에이전트", layout="centered")

    # 웹페이지 상단 제목
    st.title("🤖 Routing Agent")

    # 설명 텍스트 출력
    st.markdown(
        "사용자의 질문에 따라 적절한 에이전트를 선택하고, 최적화된 형식으로 응답합니다."
    )

    # 사용자 입력 UI 생성
    # text_input → 웹페이지에 텍스트 입력창 생성
    user_input = st.text_input("🗣️ 사용자 질문")

    # 버튼 생성
    # 버튼이 눌리면 True 반환
    if st.button("에이전트 실행") and user_input.strip():

        # 로딩 스피너 표시
        # LLM 호출 동안 "에이전트 분석 중..." 메시지 표시
        with st.spinner("에이전트 분석 중..."):

            # LLM 라우터를 이용해 질문 유형 분류
            category = llm_router_call(user_input)

            # 분류 결과 화면 출력
            st.markdown(f"🔍 **분류 결과**: `{category}`")

            # --------------------------------
            # 라우팅 맵
            # 질문 유형 → 실행할 에이전트 함수
            # --------------------------------
            ROUTING_MAP = {
                "일상": run_general_agent,
                "빠른": run_quick_agent,
                "코딩": run_coding_agent,
            }

            # 분류 결과에 따라 실행할 함수 선택
            # category가 없으면 기본적으로 general agent 사용
            final_llm_call = ROUTING_MAP.get(category, run_general_agent)

            # 선택된 에이전트 실행
            final_llm_call(user_input)
