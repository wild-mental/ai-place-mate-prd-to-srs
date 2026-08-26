---
name: 202-github-issue-handling
description: AI-Place-Mate의 GitHub 이슈·Project #25 운영 절차. 이슈 상태를 옮기거나, 일정을 바꾸거나, 태스크 데이터를 GitHub에 다시 밀 때 사용한다.
---

# GitHub 이슈 · Project 운영

## 현재 상태 — 이미 구축돼 있다

새로 만들지 않는다. 아래는 완료된 사실이다.

| 항목 | 상태 |
| --- | --- |
| 이슈 | **59건** (#1~#59) · 라벨 38종 · 마일스톤 10개 |
| 의존성 | 본문에 `#번호 (TASK-ID)` 형태로 상호 링크 |
| Project | [#25 AI-PLACE-MATE-GITHUB-PRJ](https://github.com/users/wild-mental/projects/25) · 아이템 59건 |
| 필드 | 18종 전부 주입 완료 · 압축 수행 일정과 **불일치 0건** |
| 매핑 | `tools/issue_map.json` (태스크 ID ↔ 이슈 번호) |

## 필드 구성

| 구분 | 필드 |
| --- | --- |
| 내장 재사용 | `Start date` · `Target date` · `Estimate`(일수) · `Size`(복잡도) · `Priority` · `Status` |
| 신설 | `Week` · `Track` · `Lane` · `Epic` · `Task type` · `Phase` · `Sprint` · `Critical path` · `Depends on` · `Blocks` · `Task ID` · `Complexity note` |

내장 필드를 그대로 쓰는 이유는 **GitHub Roadmap과 인사이트 차트가 이 필드를 전제**로 동작하기 때문이다.
별도 필드를 만들면 뷰마다 다시 지정해야 한다.

`Priority` 매핑 — 임계 경로 `P0`(15건) · 후행 3건 이상 `P1` · 나머지 `P2`.

## 일상 조작

```bash
gh issue view <번호>                                    # 태스크 명세 확인
gh issue list --label critical-path --state open        # 임계 경로 잔여
gh project item-list 25 --owner wild-mental --format json
```

상태 전환은 웹 UI 또는 `gh project item-edit`으로 한다.

## 도구 — 배치 작업은 스크립트로

이슈 59건에 필드 18개를 넣으면 개별 호출로는 약 940회가 되어 **GraphQL 한도(5,000점)를 태운다.**
실제로 한 번 겪었고, 그래서 아래 스크립트는 항목당 필드를 **alias로 묶어 단일 뮤테이션**으로 보낸다(59회).

| 스크립트 | 용도 |
| --- | --- |
| `tools/gh_sync_issues.py --dry <TASK-ID>` | 이슈 본문 미리보기 |
| `tools/gh_sync_issues.py --create` | 이슈 전량 생성 |
| `tools/gh_sync_issues.py --link` | 의존성을 실제 `#번호`로 치환 |
| `tools/gh_sync_issues.py --refresh-paths` | 본문의 문서 경로만 교체 (본문 재생성 없이) |
| `tools/gh_sync_project.py --fields` | 프로젝트 필드 생성 |
| `tools/gh_sync_project.py --add` | 이슈를 프로젝트에 추가 |
| `tools/gh_sync_project.py --values` | 필드 값 주입 (배치 뮤테이션) |

**본문을 통째로 재생성하지 않는다.** `--link`로 치환한 이슈 번호가 날아간다.
경로만 바꿔야 하면 `--refresh-paths`를 쓴다.

## 일정을 바꾸려면

GitHub에서 날짜를 직접 고치지 않는다. **역류하지 않기 때문에** 문서와 갈라진다.

```
tools/tasks_data.py 수정          ← 단일 원천
  → tools/gen_task_list.py        태스크 리스트 재생성 + 검증
  → tools/gen_fasttrack_plan.py   압축 일정 재산출
  → tools/export_schedule.py      /tmp/schedule.json
  → tools/gh_sync_project.py --values
```

`gen_task_list.py`가 **중복 ID · 미정의 선행 · 순환 의존성 · 스프린트 역전**을 검사하고,
하나라도 걸리면 문서를 쓰지 않는다.

## 뷰

Projects v2에는 **뷰 생성 API가 없다.** 웹에서 만든다.
설정값은 `docs/ops-docs/[Ops]GitHub-Project-View-Setup.md`에 있다 — 로드맵 · 임계 경로 · 트랙 보드 · 주차별 착수 · Phase 게이트.

## 주의

- `gh project`는 **Node ID**를 쓴다 (`PVT_...`, `PVTI_...`). 정수 번호가 아니다
- 프로젝트 조작에는 `project` 스코프가 필요하다 — `gh auth refresh -s project`
- 배치 호출 사이에 지연을 둔다. 한도에 걸리면 조용히 실패한다
