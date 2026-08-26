# [운영] GitHub Project 뷰 설정 가이드

**프로젝트:** [AI-PLACE-MATE-GITHUB-PRJ](https://github.com/users/wild-mental/projects/25)

**대상:** 이슈 59건 (`#1` ~ `#59`) · 압축 수행 일정(PLAN-AIPLACE-FAST-001) 기준

---

## 0. 왜 뷰만 수동인가

이슈·라벨·마일스톤·프로젝트 필드·필드 값은 **전부 스크립트로 채웠다.**
그러나 **GitHub Projects v2에는 뷰 생성 API가 없다** — GraphQL에 해당 뮤테이션이
존재하지 않아 `gh` CLI로도 만들 수 없다. 아래 5개 뷰는 웹에서 몇 번의 클릭으로 만든다.

**필드가 이미 준비되어 있으므로** 각 뷰는 30초 안에 완성된다.

---

## 1. 채워진 필드

| 필드 | 타입 | 값 | 출처 |
| --- | --- | --- | --- |
| **Start date** | Date | 압축 일정 착수일 | PLAN-FAST-001 §2 |
| **Target date** | Date | 압축 일정 종료일 | PLAN-FAST-001 §2 |
| **Estimate** | Number | 소요 영업일 (H5 · M3 · L1) | 태스크 리스트 §0.5 |
| **Size** | Select | 복잡도 매핑 — H→L · M→M · L→XS | 태스크 리스트 §0.5 |
| **Priority** | Select | P0 = 임계 경로 · P1 = 후행 3건 이상 · P2 = 그 외 | 후행 수 |
| **Status** | Select | 전건 `Backlog` 로 초기화 | — |
| **Week** | Number | 착수 주차 (1~13) | PLAN-FAST-001 §3 |
| **Track** | Select | 플랫폼 · 백엔드 · 프론트엔드 · 디자인 · QA | 유형 기준 배정 |
| **Lane** | Text | `backend1` 처럼 실제 작업 레인 | 자원 제약 스케줄링 |
| **Epic** | Select | INF · TEC · CTR … UX (16종) | 태스크 ID 접두어 |
| **Task type** | Select | Contract · Data · Read · Write · UI · Test · Infra · NFR · Design | 태스크 리스트 §0.3 |
| **Phase** | Select | P0 기반·계약 / P1 클로즈드 베타 / P1 말 / P2 오픈 베타 | 스프린트 → Phase |
| **Sprint** | Select | S-1 ~ S8 | 태스크 리스트 부록 B |
| **Critical path** | Select | Yes / No (15건이 Yes) | 임계 경로 계산 |
| **Depends on** · **Blocks** | Text | 태스크 ID 목록 | 의존성 원천 |
| **Task ID** | Text | `DAT-001` 형식 | — |

이슈 본문의 `Depends on` / `Blocks` 는 **실제 이슈 번호로 상호 링크**되어 있어
GitHub에서 선후 관계를 클릭으로 따라갈 수 있다.

---

## 2. 만들 뷰 5개

### 뷰 1 — 🗓️ 로드맵 (가장 먼저)

**목적:** 전체 일정을 한 화면에서 본다. 압축 수행 Gantt의 GitHub판이다.

| 설정 | 값 |
| --- | --- |
| 이름 | `🗓️ 로드맵` |
| 레이아웃 | **Roadmap** |
| Date fields | **Start date** → **Target date** |
| Markers | `Milestones` 켜기 (스프린트 마감일이 세로선으로 표시된다) |
| Group by | **Track** |
| Sort | `Start date` 오름차순 |
| Zoom | `Month` |

**만드는 법** — 프로젝트 우측 상단 `+ New view` → `Roadmap` 선택 →
표 우측 `⚙️` → `Date fields` 에서 Start/Target 지정 → `Group by` 에 Track 지정.

> Track으로 묶으면 **9개 레인이 동시에 도는 모습**이 그대로 보인다.
> 압축 일정 §2의 Gantt와 같은 그림이다.

---

### 뷰 2 — 🔥 임계 경로

**목적:** 하루 밀리면 전체가 밀리는 15건만 본다. **매일 확인하는 뷰다.**

| 설정 | 값 |
| --- | --- |
| 이름 | `🔥 임계 경로` |
| 레이아웃 | **Table** |
| Filter | `critical-path:Yes` 또는 라벨 `label:critical-path` |
| 표시 필드 | Title · Status · Start date · Target date · Track · Blocks |
| Sort | `Start date` 오름차순 |

**필터 입력란에 그대로 붙여넣기**

```
label:critical-path
```

> 15건이 순서대로 나온다. `INF-001 → INF-003 → DAT-001 → CTR-001 → QRY-002 →
> EVD-001 → RNK-001 → RNK-003 → RSV-001 → RSV-003 → RSV-005 → MCH-003 →
> AGR-001 → AGR-005 → AGR-006`

---

### 뷰 3 — 🚦 트랙 보드

**목적:** 담당자별 진행 상황. 데일리 스탠드업용.

| 설정 | 값 |
| --- | --- |
| 이름 | `🚦 트랙 보드` |
| 레이아웃 | **Board** |
| Column by | **Status** (Backlog / Ready / In progress / In review / Done) |
| Group by | **Track** |
| 표시 필드 | Task ID · Estimate · Critical path |

**주차별로 좁혀 보려면** 필터에 아래를 입력한다.

```
week:3
```

---

### 뷰 4 — 📅 주차별 착수

**목적:** 이번 주에 누가 무엇을 시작하는지. **주간 회의용.**

| 설정 | 값 |
| --- | --- |
| 이름 | `📅 주차별 착수` |
| 레이아웃 | **Table** |
| Group by | **Week** |
| 표시 필드 | Task ID · Title · Track · Lane · Estimate · Depends on |
| Sort | `Start date` 오름차순 |

> 압축 일정 §3의 «동시 작업 프로파일» 표와 같은 정보다.
> W3에 9건이 몰리는 것이 눈으로 보인다.

---

### 뷰 5 — 🧱 Phase · 게이트

**목적:** 게이트 판정 시점에 해당 Phase가 다 끝났는지 본다.

| 설정 | 값 |
| --- | --- |
| 이름 | `🧱 Phase · 게이트` |
| 레이아웃 | **Table** |
| Group by | **Phase** |
| 표시 필드 | Task ID · Status · Target date · Sprint · Critical path |
| Sort | `Target date` 오름차순 |

**게이트 판정 기준** (SRS §10.4)

| Phase | 태스크 | 게이트 통과 조건 |
| --- | --- | --- |
| P0 기반·계약 | 15건 | REQ-TEC 전건 통과 · 파싱 실패율 ≤ 3% · 결정론 히트율 ≥ 60% |
| P1 클로즈드 베타 | 25건 | WEBD ≥ 목표 60% · 불일치 신고 ≤ 15% · **가맹 LOI ≥ 30곳** |
| P1 말 | 7건 | 웹훅 멱등성 · 노쇼 오판정률 ≤ 1% |
| P2 오픈 베타 | 12건 | 제안 도착 ≥ 70% · 노쇼 ≤ 8% · **300 RPS 부하 테스트 통과** |

---

## 3. 권장 워크플로 (자동화)

프로젝트 `⚙️ Settings` → `Workflows` 에서 켠다. **API로는 설정할 수 없다.**

| 워크플로 | 설정 | 효과 |
| --- | --- | --- |
| **Item added to project** | Status → `Backlog` | 새 이슈가 자동 분류 |
| **Item reopened** | Status → `In progress` | 되돌린 작업 추적 |
| **Item closed** | Status → `Done` | 이슈를 닫으면 보드가 갱신 |
| **Pull request merged** | Status → `Done` | PR 머지로 완료 처리 |
| **Auto-add to project** | 저장소 `ai-place-mate-prd-to-srs` · `is:issue` | 이후 만든 이슈가 자동 편입 |

---

## 4. 운영 규칙

### 매일 — 임계 경로만 본다

**뷰 2(🔥 임계 경로)** 에서 15건의 Status만 확인한다. 나머지는 주간에 본다.
임계 경로 태스크가 `Target date` 를 넘기면 **그날 전체 일정이 하루 밀린 것**이다.

### 주간 — 착수표와 대조한다

**뷰 4(📅 주차별 착수)** 를 압축 일정 §3의 주차별 표와 대조한다.
밀린 것이 있으면 `Blocks` 필드로 후행 영향 범위를 즉시 계산한다.

### Phase 종료 — 게이트를 판정한다

**뷰 5(🧱 Phase · 게이트)** 에서 해당 Phase가 전건 `Done` 인지 확인하고,
위 §2 뷰 5의 표에 있는 게이트 조건을 판정한다.
**`unreliable` 로 표기된 지표는 판정에 쓰지 않는다** (SRS §10.2.5).

---

## 5. 문서와 GitHub의 동기화

| 원천 | GitHub 반영 방법 |
| --- | --- |
| `tools/tasks_data.py` (태스크·의존성·복잡도) | 수정 후 `gen_task_list.py` · `gen_fasttrack_plan.py` 재생성 |
| 일정 변경 | `export_schedule.py` → `gh_sync_project.py --values` 로 날짜 재주입 |
| 태스크 본문 변경 | `gen_task_docs.py` 재생성 후 `gh issue edit` (수동 또는 스크립트 확장) |
| 신규 태스크 | `tasks_data.py` 추가 → `gh_sync_issues.py --create` → `--link` → `--values` |

> ⚠️ **GitHub에서 직접 고친 내용은 문서로 역류하지 않는다.**
> 단일 원천은 `tools/tasks_data.py` 이며, 라벨·필드는 파생물이다.
> 계획이 바뀌면 문서를 먼저 고치고 재동기화한다.

---

**작성일 2026-08-26 · 근거 PLAN-AIPLACE-FAST-001 · TASK-AIPLACE-MVP-001 v3.2**
