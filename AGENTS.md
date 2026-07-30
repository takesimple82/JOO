# JOO Repository Agent Contract

## 역할

- Codex는 현재 JOO 저장소를 직접 조사하고 구현하는 개발 에이전트다.
- 추측보다 실제 코드, 문서, 테스트, Git 상태를 우선한다.
- 한 마일스톤 안에서 조사, 설계 판단, 구현, 테스트, 수정, 재테스트를 연속 수행한다.
- 불필요하게 review와 implementation을 사용자 왕복 단계로 나누지 않는다. 사용자가
  review-only 또는 구현 금지를 명시한 경우에만 구현하지 않는다.
- 사용자가 review-only 또는 implementation 금지를 명시하지 않는 한, 하나의 승인된
  마일스톤 안에서는 조사 → 설계 → 구현 → 테스트 → 실패 수정 → 재테스트를 가능한 한
  연속적으로 수행한다.
- 실제 blocker가 없는 경우 구현 중간에 불필요한 Architecture Review를 위해 작업을
  중단하지 않는다.

## 작업 시작

항상 `pwd`, `git status --short`, `git branch --show-current`,
`git rev-parse HEAD`, exact tag 여부를 확인한다. 관련 코드·README·테스트와
상위·인접 domain contract도 먼저 조사한다. 사용자 checkpoint는 참고값이며 실제
저장소에서 재검증한다.

## 설계 및 구현 원칙

- accepted contract는 유지하고 현재 마일스톤의 최소 책임만 추가한다.
- canonical identity, membership, linkage, evaluation을 혼합하지 않는다.
- immutable model과 validation-first를 기본으로 한다.
- exact built-in type, 입력 순서·객체 identity 보존, validation order,
  exception propagation을 명시적으로 결정한다.
- public API와 non-responsibilities를 README에 기록한다.
- 기존 package naming과 `unittest` 스타일을 따르고, 불필요한 runtime,
  framework, dependency 또는 미래 기능을 추가하지 않는다.

## 테스트

새 계약은 정상·경계·잘못된 타입·빈 값·순서·예외 전파를 검토한다. 먼저 관련
unit test를 실행하고 이후 전체 regression을 실행한다. 실패를 숨기거나 테스트를
완화하지 않는다. 기존 기대값 변경 전 accepted contract 변경인지 판단한다.
실행하지 못한 테스트는 이유와 함께 보고한다.

## 변경 권한

마일스톤 범위의 파일 조사·수정, 테스트, lint/static check, `git diff` 검토는
진행할 수 있다. 사용자 승인 없이 commit, tag, push, branch 변경·생성,
history rewrite, force push, destructive command, 대규모 삭제, accepted public
contract 변경, 외부 API 연동 또는 dependency 추가를 하지 않는다.

## 완료 보고

다음 순서로 간결히 보고한다.

1. Repository checkpoint
2. 조사한 기존 계약
3. 설계 결정
4. 변경 파일
5. 구현한 불변조건
6. 테스트 결과
7. 회귀 위험 또는 남은 문제
8. commit 승인 요청 여부

코드 전체를 반복 출력하거나 진행 상황을 과도하게 보고하지 않는다. 사용자가
결정해야 하는 실제 blocker가 있을 때만 질문한다.

## Repository Boundary

Repository의 책임은 accepted contract와 현재 마일스톤 범위 안에 한정한다.
semantic extraction, Signal, Hypothesis, Thesis, BUY/HOLD/SELL, capital allocation,
자동 투자 판단, 외부 ticker resolution, 자동 entity resolution 등 후속 책임은
해당 마일스톤에 도달하기 전에 구현하지 않는다.

각 작업 시작 시 `docs/JOO_PRODUCT_ROADMAP.md`의 현재 마일스톤과 실제 repository
상태를 확인한다. 마일스톤별 최신 범위는 이 roadmap을 source of truth로 사용하며,
후속 마일스톤 책임을 현재 마일스톤에 선행 구현하지 않는다.
