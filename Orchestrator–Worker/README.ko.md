## 개선 사항: LLM JSON 파싱 안정성 개선

### 문제

기존 구현에서는 LLM 응답을 그대로 `json.loads()`로 파싱했다.

하지만 실제 LLM 응답은 다음과 같은 문제가 자주 발생했다.

- ```json 코드 블록 포함
- JSON 앞뒤에 설명 텍스트 존재
- JSON 외 텍스트 혼합

이로 인해 다음과 같은 오류가 발생했다.

- JSONDecodeError
- Extra data error
- 프로그램 실행 중단

---

### 해결 방법

LLM 응답에서 **JSON 영역만 추출하는 함수**를 추가했다.

코드 블록과 불필요한 텍스트를 제거한 뒤  
정규식을 사용해 JSON 부분만 파싱하도록 수정했다.

---

### 변경 구조

Before

LLM response → json.loads()

After

LLM response  
→ 코드 블록 제거  
→ JSON 영역 추출  
→ json.loads()

---

### 주요 변경 사항

- `extract_json()` 함수 추가
- ```json 코드 블록 제거
- 정규식 기반 JSON 추출
- JSON 파싱 안정성 향상

---

### 장점

- JSON 파싱 오류 감소
- 다양한 LLM 응답 형식 대응
- 시스템 안정성 향상

---

## 개선 사항: Worker 응답 구조 정규화

### 문제

Worker 응답은 항상 동일한 구조가 아니었다.

LLM은 다음과 같은 다양한 형식으로 응답할 수 있다.

- dict
- list[dict]
- plain text

이로 인해 다음 문제가 발생했다.

- TypeError
- Worker output parsing failure
- 프로그램 중단

---

### 해결 방법

Worker 응답을 **표준 구조로 변환하는 normalize 과정**을 추가했다.

---

### 변경 구조

Before

Worker → 다양한 응답 구조

After

Worker → normalize  
→ answer  
→ sources

---

### 주요 변경 사항

- `normalize_worker_output()` 함수 추가
- list 응답 처리
- dict 응답 처리
- text 응답 fallback 처리

---

### 장점

- Worker 응답 구조 통일
- 파싱 오류 감소
- 에이전트 안정성 향상

---

## 개선 사항: 파싱 실패 시 fallback 처리

### 문제

기존 코드에서는 JSON 파싱 실패 시 프로그램이 즉시 종료되었다.

예시 오류

- JSONDecodeError
- Worker output must be dict

---

### 해결 방법

JSON 파싱 실패 시 **fallback 로직을 추가**했다.

---

### 변경 구조

Before

JSON parse 실패 → 프로그램 종료

After

JSON parse 실패  
→ raw response 사용  
→ sources 빈 배열 처리

---

### 주요 변경 사항
 try:
parsed = extract_json(raw)
answer, sources = normalize_worker_output(parsed)

except Exception:

answer = raw
sources = []


---

### 장점

- 프로그램 crash 방지
- LLM 응답 형식 변화 대응
- 안정적인 에이전트 실행

---

## 개선 사항: 출처(Source) 중복 제거

### 문제

여러 Worker가 동일한 자료를 가져오는 경우가 많았다.

예시

Worker1 → openai.com  
Worker2 → openai.com  
Worker3 → openai.com

이 경우 최종 결과에 동일한 출처가 반복된다.

---

### 해결 방법

모든 출처를 수집한 뒤 **deduplicate 처리**를 수행했다.

---

### 변경 구조

Before

sources → 그대로 출력

After

sources  
→ merge  
→ deduplicate  
→ 출력

---

### 주요 변경 사항

unique_sources = list(set(all_sources))


---

### 장점

- 중복 출처 제거
- 결과 가독성 향상
- 연구 결과 정리 개선

---

## 개선 사항: 병렬 Worker 실행 구조 유지

### 기존 구조

Worker를 순차적으로 실행할 경우 리서치 속도가 느려진다.

---

### 개선 구조

Worker를 **asyncio 기반 병렬 실행**하도록 유지했다.

---

### 실행 방식
responses = await asyncio.gather(*tasks)


---

### 장점

- 조사 속도 향상
- 다양한 자료 탐색 가능
- 멀티 에이전트 구조 유지

---

## 개선 결과

위 개선을 통해 다음 문제들이 해결되었다.

- JSON 파싱 오류
- Worker 응답 구조 불안정
- 프로그램 crash
- 출처 중복 문제

결과적으로 시스템은 **더 안정적인 Orchestrator–Worker Research Agent 구조**로 동작하게 되었다.


