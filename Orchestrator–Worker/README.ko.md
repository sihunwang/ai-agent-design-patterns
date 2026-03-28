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


### 실행 방식
responses = await asyncio.gather(*tasks)

---

### 장점

- 조사 속도 향상
- 다양한 자료 탐색 가능
- 멀티 에이전트 구조 유지

---

## 개선 결과

 **더 안정적인 Orchestrator–Worker Research Agent 구조**로 동작하게 되었다.


