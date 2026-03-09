# ai-agent-design-patterns

## AI 에이전트 설계 패턴 (From Scratch → Frameworks)

### 이 저장소를 만든 이유
이 프로젝트의 목표는  
AI 에이전트를 **어떻게 사용하는지**가 아니라  
**어떻게 설계하는지**를 이해하는 것입니다.

이 저장소에서는 LLM 기반 AI 에이전트의 핵심 워크플로 패턴을 다음 두 가지 방식으로 구현합니다.

- 순수 Python 코드로 직접 구현 (from scratch)  
- LangChain, LangGraph 등 현대적인 프레임워크로 재구현  

---

## 핵심 AI 에이전트 워크플로 패턴

각 패턴은 두 가지 버전으로 구현되어 있습니다.

- `from_scratch.py`  
  → 추상화 없이, 최소한의 Python 코드로 구현  

- `framework_version.py`  
  → LangChain / LangGraph / SDK 기반 구현  

### 구현된 패턴 목록

- 프롬프트 체이닝 (Prompt Chaining)  
- 라우팅 (Routing)  
- 병렬 실행 (Parallel Execution)  
- 오케스트레이터–워커 구조 (Orchestrator–Worker)  
- 평가–최적화 루프 (Evaluation–Optimization)  
- ReAct (추론 + 행동)  
- 계획–실행 분리 (Plan–Execute Separation)  

---

## 저장소 구조

```text
src/
├─ common/
│  ├─ llm.py           # LLM 호출을 위한 최소 래퍼
│  ├─ prompts.py       # 공통 프롬프트 템플릿
│  └─ utils.py
│
├─ pattern_01_prompt_chaining/
│  ├─ from_scratch.py
│  └─ langchain_version.py
│
├─ pattern_02_routing/
├─ pattern_03_parallel/
├─ pattern_04_orchestrator_worker/
├─ pattern_05_eval_optimize/
├─ pattern_06_react/
└─ pattern_07_plan_execute/
