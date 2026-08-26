---
name: 400-task-execution-workflow
description: docs/tasks 의 태스크 명세 59건을 실제 구현으로 옮기는 절차. 태스크를 시작·진행·완료할 때, 그리고 무엇부터 할지 고를 때 사용한다.
---

# 태스크 실행 워크플로

이 저장소는 **기획이 끝난 상태**다. 태스크 59건과 의존 관계·일정이 모두 확정돼 있다.
구현자가 할 일은 새로 정하는 게 아니라 **정해진 것을 순서대로 끝내는 것**이다.

## 원천 문서

| 문서 | 무엇을 답하는가 |
| --- | --- |
| `docs/plan-docs/[TaskList]AI-Place-Mate-Task-List.md` | 태스크 59건 · 선행/후행 · 복잡도 |
| `docs/tasks/<TASK-ID>.md` | **각 태스크를 어떻게** 끝내는가 (AC · DoD · 실패 시나리오) |
| `docs/plan-docs/[Plan]AI-Place-Mate-Execution-Plan.md` | 실행 전략 · DAG · 자원 제약 일정 (6명 · 72일) |
| `docs/plan-docs/[Plan]AI-Place-Mate-Fast-Track-Schedule.md` | 최대 병렬 압축안 (9명 · 63일) — GitHub Project 날짜의 원천 |
| GitHub Project #25 | 현재 상태 · 담당 · 실제 진행 |

## 1. 무엇부터 하는가

1. GitHub Project #25에서 **선행이 모두 Done인 태스크**를 고른다
2. 동률이면 `Critical path = Yes`를 먼저 잡는다 — 15건이 임계 경로에 있고, 밀리면 전체가 밀린다
3. 그 다음 우선순위는 `Blocks` 수다. 후행이 많을수록 먼저 끝내야 병목이 풀린다

**선행이 안 끝난 태스크를 시작하지 않는다.** 의존 관계는 추정이 아니라 문서에 확정돼 있다.

## 2. 시작하기 전에 읽는다

- `docs/tasks/<TASK-ID>.md` 전체 — 특히 **실패 시나리오**. AC만 보면 절반만 구현하게 된다
- 태스크가 참조하는 SRS 절 (REQ-FUNC / REQ-NF / REQ-TEC)
- 참조된 설계 다이어그램 (ERD · 시퀀스 · 플로우차트)

읽은 결과가 태스크 문서와 어긋나면 **구현을 시작하기 전에** 그 사실을 밝힌다.

## 3. 브랜치와 이슈

```bash
gh issue view <번호>                       # 태스크 ID ↔ 이슈 번호는 tools/issue_map.json
git switch -c feat/<번호>-<task-id-소문자>  # 예: feat/12-tec-001
```

- 이슈 번호를 브랜치에 남긴다 — Project #25가 이슈 단위로 돈다
- Project의 `Status`를 `In progress`로 옮긴다
- 상세는 스킬 `200-git-commit-push-pr`

## 4. 구현

- 스킬 `300-tech-constraints-guardrails`로 **제약 위반을 먼저 차단**한다
- 서버 코드 배치는 스킬 `301-server-boundary-rules`
- 데이터 접근은 스킬 `302-data-access-rules`
- AI 호출은 스킬 `303-ai-integration-rules`
- 테스트는 스킬 `tdd` — 실패 시나리오가 그대로 테스트 케이스가 된다

**태스크 문서에 없는 기능을 만들지 않는다.** 필요해 보이면 태스크로 만들어 제안한다.

## 5. 완료 판정

태스크 문서의 DoD가 우선한다. 공통 항목:

- AC 전항 충족 — **실패 시나리오 포함**
- 타입 검사 · 린트 통과
- 테스트 추가. 외부 경계는 계약 테스트로 고정
- `scripts/verify-constraints.mjs` 통과 (REQ-TEC 위반 0건)
- 문서와 실제가 어긋났으면 문서를 고친다

## 6. 마무리

```bash
gh pr create --draft --title "..." --body "..."   # Closes #<번호>
```

- PR 본문에 **의미 단위 요약**을 쓴다. 파일 나열이 아니라 무엇이 왜 바뀌었는지
- Project `Status`를 `In review`로
- 머지 후 `Done`. 후행 태스크가 풀린다

## 문서 ↔ GitHub 동기화

| 방향 | 방법 |
| --- | --- |
| 문서 → GitHub | `tools/gh_sync_issues.py` · `tools/gh_sync_project.py` |
| 일정 재산출 | `tools/gen_fasttrack_plan.py` → `tools/export_schedule.py` → `--values` |

⚠️ **GitHub에서 직접 고친 내용은 문서로 역류하지 않는다.**
일정·의존성을 바꿔야 하면 `tools/tasks_data.py`를 고치고 생성기를 다시 돌린다.
태스크 리스트 문서는 **생성물이므로 직접 편집하지 않는다.**

## 원천

- `docs/ops-docs/[Ops]GitHub-Project-View-Setup.md` — 뷰 구성과 운영 리듬
- `docs/analysis-docs/[Analysis]Task-Extraction-Methodology.md` — 태스크가 어떻게 추출됐는지
