import requests
from utils import llm_call  # LLM 호출 함수 (동기 방식)

# ================================
# 요약 함수
# ================================
def summarize_text(text, feedback_history=None):
    """
    주어진 원문(text)을 요약하는 함수

    feedback_history:
    - 이전 시도에서 FAIL 받은 요약 + 피드백 기록
    - 있으면 이를 반영해서 더 나은 요약을 생성하도록 유도
    """

    if feedback_history:
        # 이전 피드백까지 반영해서 더 좋은 요약 생성 요청
        prompt = (
            f"아래 내용을 요약해줘.\n"
            f"## 원문: {text}\n"
            f"## 이전 요약문 및 피드백 전체 기록:\n{feedback_history}\n"
            f"이전 피드백을 모두 참고해 평가 결과가 PASS가 되도록 요약문을 생성해."
        )
    else:
        # 첫 시도: 단순 요약
        prompt = f"아래 내용을 요약해줘.\n원문: {text}"

    # LLM 호출해서 요약 생성
    summary = llm_call(prompt)

    return summary

# ================================
# 평가 기준 프롬프트
# ================================
EVALUATOR_PROMPT = """
        평가 기준에 따라 다음 요약문을 엄격하게 심사해.

        1. 형식:
        - 여러 항목으로 된 개조식이어야 하며, 한 문장이라도 개조식이 아니면 무조건 FAIL

        2. 내용:
        - 정의 또는 원리, 주요 장점, 활용 예 등 3가지 핵심 요소가 모두 포함되면 PASS
        - 사소한 세부 내용, 인용, 부연 설명 누락은 FAIL이 아님

        3. 표현:
        - 모든 항목은 짧고 명확해야 함
        - 불필요한 수식, 반복문, 비문, 맞춤법/띄어쓰기 오류가 2개 이상이면 FAIL

        위 기준 중 하나라도 미달이면 반드시 FAIL을 부여해.

        응답 양식:
        - 평가 결과: PASS / FAIL
        - 문제점 및 개선 방향: (FAIL인 경우 구체적으로)
    """


# ================================
# 평가 함수: EVALUATOR_PROMPT를 사용해서 평가 결과를 알려준다
# ================================
def evaluate_summary(content, summary):
    """
    생성된 요약(summary)을 평가하는 함수

    content: 원문
    summary: 요약 결과

    → evaluator LLM이 PASS / FAIL 판단
    """

    # 평가용 프롬프트 구성
    prompt = (
        f"{EVALUATOR_PROMPT}\n\n"
        f"<원문>\n{content}\n\n"
        f"<요약문>\n{summary}"
    )

    # LLM으로 평가 수행
    return llm_call(prompt)


# ================================
# 반복 워크플로 (핵심 로직)
# ================================
def loop_workflow(content, max_retries=5): #content: 요약할것
    """
    요약 → 평가 → 개선 반복 구조

    max_retries:
    - 최대 반복 횟수
    """

    feedback_history = ""  # 이전 시도 기록 저장

    for i in range(max_retries):
        # 1. 요약 생성
        summary = summarize_text(content, feedback_history=feedback_history)

        # 2. 요약 평가
        evaluation = evaluate_summary(content, summary)

        # 중간 결과 출력 (디버깅용)
        print(f"\n요약 결과:\n{summary}\n")
        print(f"평가 결과:\n{evaluation}\n")

        # 3. PASS 여부 확인
        if "평가 결과: PASS" in evaluation: # 문자열 전체에서 부분 문자열 찾기 (줄 개념 없음)
            print("✅ 통과! 최종 요약 반환\n", summary)
            return summary

        # 4. FAIL이면 → 피드백 기록 누적
        feedback_history += (
            f"\n\n[시도 {i+1}]\n"
            f"- 요약문:\n{summary}\n"
            f"- 평가 피드백:\n{evaluation}\n"
        )

    # 최대 반복 횟수 초과 시
    print("❌ 최대 시도 도달. 마지막 요약 반환")
    return summary


# ================================
# 실행 부분 (엔트리 포인트)
# ================================
if __name__ == "__main__":

    # 1. 원문 가져오기 (GitHub raw 파일)
    url = "https://raw.githubusercontent.com/dabidstudio/sample_files/refs/heads/main/sample_wiki_text.md"
    content = requests.get(url).text

    # 앞부분 일부 출력 (확인용)
    print("📝 원문(앞부분):\n", content[:300], "\n...")

    # 2. 반복 워크플로 실행
    loop_workflow(content, max_retries=5)