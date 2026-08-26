---
description: 개발 규범 — 작업 진입 절차, 성능 기준, 계층 규칙, 완료 정의
globs: ["**/*"]
alwaysApply: true
---
# Development Guidelines

## 작업 진입 절차

이 저장소는 **기획이 끝난 상태**다. 코드를 쓰기 전에 읽을 것이 정해져 있다.

1. `docs/plan-docs/[TaskList]AI-Place-Mate-Task-List.md` 에서 태스크 ID와 선행 관계를 확인한다
2. `docs/tasks/<TASK-ID>.md` 에서 Acceptance Criteria와 실패 시나리오를 읽는다
3. 태스크가 참조하는 SRS 절과 설계 다이어그램을 읽는다
4. **선행 태스크가 끝나지 않았으면 시작하지 않는다**

없는 기능을 만들지 않는다. 태스크 문서에 없는 것을 구현했다면 그건 범위 이탈이다.

## Version Control

- **Branching:** `<type>/<issue-number>-<short-description>` (예: `feat/12-tec-001-app-scaffold`)
- **Commit:** Conventional Commits. 원자적으로, 각 커밋이 빌드되는 상태로
- **main 직접 커밋 금지.** 이슈 번호를 브랜치에 남긴다 — GitHub Project #25가 이슈 단위로 돈다
- 상세는 스킬 `200-git-commit-push-pr`

## 계층 규칙

C-TEC-002가 서버 진입점을 셋으로 제한한다. **어디에 쓸지는 취향이 아니라 표로 결정된다.**

| 상황 | 선택 | 이유 |
| --- | --- | --- |
| 화면 렌더용 읽기 | RSC 직접 조회 | 왕복이 없고 비밀값이 서버에 머문다 |
| 사용자 변경 작업 | Server Action | 타입 안전 · 점진적 향상 · POST 전용 |
| 외부 시스템 수신 (웹훅 · Cron) | Route Handler | 외부에서 HTTP로 들어온다 |
| 캐시 가능한 GET | Route Handler | Server Action은 항상 POST라 HTTP 캐시가 없다 |

**모듈 경계** — `src/modules/<name>/index.ts` 가 유일한 공개 표면이다 (REQ-TEC-002).
다른 모듈의 내부 파일을 직접 import하지 않는다. 모듈 간 통신은 함수 직접 호출이다 (D-02).

## Performance Standards (NFR)

| 기준 | 값 | 근거 |
| --- | --- | --- |
| 결정론 경로 응답 | p95 ≤ 1,000ms | REQ-NF-001a |
| LLM 폴백 경로 응답 | p95 ≤ 2,500ms | REQ-NF-001b |
| `use cache` 히트율 | ≥ 70% | REQ-NF-002 |
| 파싱 캐시 히트율 | ≥ 60% | REQ-NF-002b — LLM 비용을 잡는 캐시 |
| 처리량 | Phase 1 300 RPS → Phase 2 3,000 RPS | REQ-NF-003 (플랜 상향 전제) |

**응답 시간이 두 갈래인 이유** — LLM 왕복이 파싱 예산을 구조적으로 초과한다.
그래서 결정론 파서가 먼저 처리하고(흡수율 ≥ 70%) 실패분만 Gemini가 받는다 (ADR-T02).
이 순서를 뒤집으면 NFR이 깨진다.

## Security

- 비밀값은 서버에만 둔다. `NEXT_PUBLIC_` 접두는 공개해도 되는 값에만 쓴다
- RLS를 우회하는 경로를 만들지 않는다. Service Role 키는 Route Handler에서도 최소 범위로
- 사용자 입력은 스키마로 검증한 뒤 도메인에 들인다 (Server Action 인자는 신뢰할 수 없다)

## Code Comments

- WHY를 쓴다. WHAT은 코드가 말한다
- 쓸모없어진 주석은 즉시 지운다
- 상세는 스킬 `201-code-commenting`

## Definition of Done

태스크 문서의 DoD가 우선한다. 공통 항목은 아래와 같다.

- Acceptance Criteria 전항 충족 — **실패 시나리오 포함**
- 타입 검사와 린트 통과
- 테스트 추가 (스킬 `tdd` 참조). 외부 경계는 계약 테스트로 고정
- `scripts/verify-constraints.mjs` 통과 — REQ-TEC 위반 0건
- 관련 문서 갱신 (SRS·설계 문서가 실제와 어긋나면 문서를 고친다)

## See also

- [001-project-overview.md](001-project-overview.md) · [002-tech-stack.md](002-tech-stack.md)
- 스킬 `300-tech-constraints-guardrails` — 제약 위반 자가 점검
