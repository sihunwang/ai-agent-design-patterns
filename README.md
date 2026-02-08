# ai-agent-design-patterns
[Try Korean: 한국어 README 보기](README.ko.md)

## AI Agent Design Patterns (From Scratch → Frameworks)

### Why this repository exists

Most AI agent tutorials start with frameworks.  
This repository starts **before** that.

The goal is to understand **how AI agents are designed**, not just how they are used.

This project explores core LLM-based agent workflow patterns by:

- implementing them **from scratch in pure Python**, and  
- re-implementing the same logic using modern frameworks such as **LangChain** and **LangGraph**.

Frameworks change.  
**Design patterns last.**

---

## Core Agent Workflow Patterns

Each pattern is implemented in two versions:

- `from_scratch.py` — minimal Python, no abstraction  
- `framework_version.py` — LangChain / LangGraph / SDK-based

### Implemented Patterns

- Prompt Chaining  
- Routing  
- Parallel Execution  
- Orchestrator–Worker  
- Evaluation–Optimization  
- ReAct (Reason + Act)  
- Plan–Execute Separation  

---

## Repository Structure

```text
src/
├─ common/
│  ├─ llm.py           # raw LLM call wrapper
│  ├─ prompts.py       # shared prompt templates
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
