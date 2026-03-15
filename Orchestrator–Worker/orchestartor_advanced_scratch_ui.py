import streamlit as st
import asyncio
import json
import re
from utils import llm_call, llm_search_async


# =====================================
# JSON 추출 (가장 안전한 방식)
# =====================================
def extract_json(text):

    text = text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")

    match = re.search(r"\{[\s\S]*\}|\[[\s\S]*\]", text)

    if not match:
        raise ValueError("JSON not found in LLM output")

    json_text = match.group()

    return json.loads(json_text)


# =====================================
# worker output normalize
# =====================================
def normalize_worker_output(parsed):

    # list 형태 처리
    if isinstance(parsed, list):

        if len(parsed) == 0:
            return "", []

        parsed = parsed[0]

    # dict 아니면 fallback
    if not isinstance(parsed, dict):

        return str(parsed), []

    answer = parsed.get("answer", "")
    sources = parsed.get("sources", [])

    if not isinstance(sources, list):
        sources = []

    return answer, sources


# =====================================
# orchestrator prompt
# =====================================
def get_orchestrator_prompt(user_query):

    return f"""
다음 질문을 분석하고 필요 만큼 하위 질문으로 분해해.

반드시 JSON 배열만 출력해.

[
  {{
    "question": "하위 질문",
    "description": "질문의 의도"
  }}
]

사용자 질문: {user_query}
"""


# =====================================
# worker prompt
# =====================================
def get_worker_prompt(user_query, question, description):

    return f"""
다음 하위 질문을 조사해.

사용자 질문: {user_query}
하위 질문: {question}
의도: {description}

웹 검색을 활용해 조사하고 반드시 JSON 형식으로 응답해.

{{
 "answer": "분석 결과",
 "sources": [
  "URL1",
  "URL2"
 ]
}}
"""


# =====================================
# 병렬 실행
# =====================================
async def run_llm_parallel(prompt_details):

    tasks = [
        llm_search_async(item["user_prompt"], item["model"]) for item in prompt_details
    ]

    responses = await asyncio.gather(*tasks)

    return responses


# =====================================
# Agent workflow
# =====================================
async def run_orchestrator_workflow_streamlit(user_query):

    # 1 질문 분해
    st.subheader("1. Question Decomposition")

    orchestrator_prompt = get_orchestrator_prompt(user_query)

    orchestrator_response = llm_call(orchestrator_prompt, model="gpt-4o")

    subtask_list = extract_json(orchestrator_response)

    st.json(subtask_list)

    # 2 worker prompt 생성
    worker_prompt_details = []

    for subtask in subtask_list:

        worker_prompt_details.append(
            {
                "user_prompt": get_worker_prompt(
                    user_query, subtask["question"], subtask["description"]
                ),
                "model": "gpt-4.1",
            }
        )

    # 3 worker 병렬 실행
    st.subheader("2. Parallel Research")

    raw_responses = await run_llm_parallel(worker_prompt_details)

    worker_answers = []
    all_sources = []

    columns = st.columns(len(subtask_list))

    for col, subtask, raw in zip(columns, subtask_list, raw_responses):

        try:

            parsed = extract_json(raw)

            answer, sources = normalize_worker_output(parsed)

        except Exception:

            answer = raw
            sources = []

        worker_answers.append(answer)
        all_sources.extend(sources)

        with col:

            st.markdown(f"### {subtask['question']}")

            st.write(answer)

            if sources:

                with st.expander("Sources"):

                    for s in sources:
                        st.write(s)

    # 4 source dedupe
    unique_sources = list(set(all_sources))

    # 5 aggregator
    st.subheader("3. Final Report")

    aggregator_prompt = f"""
다음 정보를 종합해 최종 보고서를 작성해.

사용자 질문: {user_query}

"""

    for q, ans in zip(subtask_list, worker_answers):

        aggregator_prompt += f"\n질문: {q['question']}\n"
        aggregator_prompt += f"답변: {ans}\n"

    final_response = llm_call(aggregator_prompt, model="gpt-4.1")

    st.write(final_response)

    # sources
    st.markdown("### Sources")

    for s in unique_sources:

        st.write(s)


# =====================================
# streamlit main
# =====================================
def main():

    st.set_page_config(page_title="Research Agent", layout="wide")

    st.title("Orchestrator Worker Research Agent")

    default_query = "2026년 AI Agent는 어떻게 발전했을까?"

    user_query = st.text_input("사용자 질문", value=default_query)

    if st.button("Run Agent"):

        asyncio.run(run_orchestrator_workflow_streamlit(user_query))


if __name__ == "__main__":
    main()
