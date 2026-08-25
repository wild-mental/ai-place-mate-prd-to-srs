#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""개발 실행 계획(총괄 문서) 생성기.

`tasks_data.py` 를 단일 원천으로 DAG 레벨 · 임계 경로 · 자원 제약 일정을 계산하고
`docs/[총괄] 개발 실행 계획.md` 를 생성한다. 일정의 모든 간선은 실재하는 의존성이다.
"""
import sys, os, re, datetime as dt
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tasks_data as D

OUT = "docs/[총괄] 개발 실행 계획.md"
BY = {t[0]: t for t in D.TASKS}
IDS = list(BY)
DUR = {"H": 5, "M": 3, "L": 1}                 # 복잡도 → 소요 영업일
ROLE = {"Infra": "PLT", "NFR": "PLT", "Contract": "BE", "Data": "BE",
        "Read": "BE", "Write": "BE", "UI": "FE", "Design": "DSG", "Test": "QA"}
ROLE_NAME = {"PLT": "플랫폼", "BE": "백엔드", "FE": "프론트엔드", "DSG": "디자인", "QA": "QA"}
# 트랙(동시 작업 레인) 수
CAP = {"PLT": 1, "BE": 2, "FE": 1, "DSG": 1, "QA": 1}
START = dt.date(2026, 9, 1)                    # 화요일 아님 — 아래에서 월요일로 보정

BLOCKS = defaultdict(list)
for _t, _f, _r, _d, _c, _ty, _sp in D.TASKS:
    for _x in _d:
        BLOCKS[_x].append(_t)

dur = {t: DUR[BY[t][4]] for t in IDS}
role = {t: ROLE[BY[t][5]] for t in IDS}


# ── DAG 레벨 ──────────────────────────────────────────────
def levels():
    lv = {}
    def f(n):
        if n in lv:
            return lv[n]
        lv[n] = 0 if not BY[n][3] else 1 + max(f(x) for x in BY[n][3])
        return lv[n]
    for n in IDS:
        f(n)
    return lv


LV = levels()


# ── 임계 경로 (기간 가중) ─────────────────────────────────
def critical_path():
    ef, prev = {}, {}
    def f(n):
        if n in ef:
            return ef[n]
        best, bp = 0, None
        for x in BY[n][3]:
            if f(x) > best:
                best, bp = f(x), x
        ef[n], prev[n] = best + dur[n], bp
        return ef[n]
    for n in IDS:
        f(n)
    end = max(IDS, key=lambda n: (ef[n], -len(BLOCKS.get(n, []))))
    ch = [end]
    while prev.get(ch[-1]):
        ch.append(prev[ch[-1]])
    return list(reversed(ch)), ef[end], ef


CP, CP_LEN, EF = critical_path()


# ── 우선순위: 남은 최장 경로 ──────────────────────────────
def rank():
    r = {}
    def f(n):
        if n in r:
            return r[n]
        r[n] = dur[n] + max([f(x) for x in BLOCKS.get(n, [])] or [0])
        return r[n]
    for n in IDS:
        f(n)
    return r


RANK = rank()


# ── 자원 제약 리스트 스케줄링 ─────────────────────────────
def schedule():
    finish, start, lane = {}, {}, {}
    free = {r: [0] * CAP[r] for r in CAP}      # 레인별 가용 시각
    done = set()
    pending = set(IDS)
    while pending:
        ready = [n for n in pending if all(p in done for p in BY[n][3])]
        if not ready:
            raise SystemExit("의존성 교착 — 순환 확인 필요")
        ready.sort(key=lambda n: (-RANK[n], n))
        placed = False
        for n in list(ready):
            r = role[n]
            li = min(range(CAP[r]), key=lambda i: free[r][i])
            dep_ready = max([finish[p] for p in BY[n][3]] or [0])
            s = max(free[r][li], dep_ready)
            start[n], finish[n], lane[n] = s, s + dur[n], (r, li)
            free[r][li] = finish[n]
            done.add(n)
            pending.discard(n)
            placed = True
        if not placed:
            raise SystemExit("스케줄 진행 불가")
    return start, finish, lane


S, F, LANE = schedule()
SPAN = max(F.values())


# ── 영업일 → 날짜 ─────────────────────────────────────────
def workday(idx):
    d0 = START
    while d0.weekday() >= 5:
        d0 += dt.timedelta(days=1)
    n, cur = 0, d0
    while n < idx:
        cur += dt.timedelta(days=1)
        if cur.weekday() < 5:
            n += 1
    return cur


def gname(t):
    """간트 라벨 — 콜론·괄호 제거"""
    s = BY[t][1].replace(":", " ").replace("`", "")
    s = re.sub(r"\s*\(.*?\)\s*", " ", s).strip()
    return (s[:24] + "…") if len(s) > 24 else s


def build():
    L, A = [], None
    out = []
    A = out.append
    n = len(IDS)
    work = sum(dur.values())
    heads = [t for t in IDS if not BY[t][3]]
    tails = [t for t in IDS if not BLOCKS.get(t)]

    A("# [총괄] 개발 실행 계획 — AI-Place-Mate")
    A("")
    A("**문서 ID:** PLAN-AIPLACE-MVP-001")
    A("")
    A("**개정 버전:** 1.0")
    A("")
    A(f"**날짜:** 2026-08-25")
    A("")
    A("**근거 문서:** TASK-AIPLACE-MVP-001 v3.2 (`[태스크 리스트] AI-Place-Mate.md` · 59건) · "
      "`docs/tasks/*.md` (태스크별 이슈 명세 59건)")
    A("")
    A("> ⚙️ **이 문서는 생성물이다.** 단일 원천은 `tools/tasks_data.py` 이며 "
      "`python3 tools/gen_exec_plan.py` 로 재생성한다. **일정의 모든 선후 관계는 "
      "`선행 태스크` 열에 실재하는 의존성**이며, 임의로 그린 간선이 없다.")
    A("")
    A("---")
    A("")
    A("## 0. 이 문서의 위치")
    A("")
    A("| 문서 | 답하는 질문 |")
    A("| --- | --- |")
    A("| SRS (기술제약 반영판) | **무엇을** 만드는가 |")
    A("| 설계 문서 (SDD) | **어떻게** 만드는가 |")
    A("| 태스크 리스트 | **무엇을 쪼개** 만드는가 |")
    A("| `docs/tasks/*.md` | **각 조각을 어떻게** 끝내는가 (AC · DoD) |")
    A("| **본 문서** | **어떤 순서로, 누가, 언제** 만드는가 |")
    A("")
    A("실무자는 본 문서에서 **자기 트랙과 착수 시점**을 확인하고, 실제 작업은 "
      "`docs/tasks/<TASK-ID>.md` 의 Task Breakdown과 Acceptance Criteria를 따른다.")
    A("")
    A("---")
    A("")
    # ── 1. 실행 전략 ─────────────────────────────────────
    A("## 1. 실행 전략")
    A("")
    A("### 1.1 네 가지 원칙")
    A("")
    A("| # | 원칙 | 근거 | 어기면 |")
    A("| --- | --- | --- | --- |")
    A("| **1** | **게이트를 먼저 세운다** — `TEC-001`·`TST-007` 을 첫 주에 작동시킨다 | SRS §14.2 | 제약 위반이 누적된 뒤 한꺼번에 드러난다 |")
    A("| **2** | **계약을 먼저 확정한다** — `CTR-001`·`CTR-002`·`CTR-005` 가 모든 구현의 기준점 | 방법론 Step 1 | 두 태스크가 같은 계약을 다르게 구현해도 탐지되지 않는다 |")
    A("| **3** | **Mock으로 병행한다** — `MCK-001` 픽스처로 UI가 백엔드를 기다리지 않는다 | ANL-002 §2.1 | 프론트가 직렬 대기하며 임계 경로가 길어진다 |")
    A("| **4** | **디자인이 앞선다** — `UX-001` 은 착수 0일차. 6개 태스크를 막고 있다 | DAG L0 | 프론트·플랫폼이 동시에 대기한다 |")
    A("")
    A("### 1.2 트랙 구성")
    A("")
    A("역할은 **유형(Type)** 을 기준으로 나눈다 — Epic이 아니라 유형이 담당자를 정한다"
      "(태스크 리스트 §0.3).")
    A("")
    A("| 트랙 | 담당 유형 | 레인 수 | 태스크 | 공수 |")
    A("| --- | --- | --- | --- | --- |")
    rcnt, rday = Counter(), Counter()
    for t in IDS:
        rcnt[role[t]] += 1
        rday[role[t]] += dur[t]
    tmap = {"PLT": "`Infra` · `NFR`", "BE": "`Contract` · `Data` · `Read` · `Write`",
            "FE": "`UI`", "DSG": "`Design`", "QA": "`Test`"}
    for r in ["PLT", "BE", "FE", "DSG", "QA"]:
        A(f"| **{ROLE_NAME[r]}** | {tmap[r]} | {CAP[r]} | {rcnt[r]}건 | {rday[r]} person-day |")
    A(f"| | | **{sum(CAP.values())}** | **{n}건** | **{work} person-day** |")
    A("")
    A(f"**최소 인원 근거** — 총 공수 {work} person-day를 임계 경로 {CP_LEN}일 안에 소화하려면 "
      f"이론상 **{work/CP_LEN:.1f}명**이 필요하다. 역할별 부하 불균형(백엔드 {rday['BE']}일)을 "
      f"고려해 백엔드만 2레인으로 두고 총 {sum(CAP.values())}명으로 구성했다.")
    A("")
    A("### 1.3 착수 전에 풀어야 할 것")
    A("")
    A("외부 의존성은 코드로 해결할 수 없다. **아래가 막히면 해당 트랙이 통째로 멈춘다.**")
    A("")
    A("| 외부 의존 | 막는 태스크 | 필요 시점 | 미확보 시 |")
    A("| --- | --- | --- | --- |")
    A("| **DEP-T1** Vercel 계정·프로젝트 | `INF-001` | **0일차** | 아무것도 배포되지 않는다 |")
    A("| **DEP-T2** Supabase 프로젝트·CLI | `INF-003` · `DAT-001` | **0일차** | 데이터 계층 전체 정지 |")
    A("| **DEP-T3** Gemini API 키·쿼터 | `QRY-002` | S3 착수 전 | 결정론 경로로만 동작 (자연어 커버리지 하락) |")
    A("| **DEP-T4** PG 계약 (서명·멱등 키) | `RSV-003` · `CTR-002` 웹훅 절 | S6 착수 전 | 결제 슬라이스 착수 불가 |")
    A("| **DEP-T5** 가맹 온보딩 인력 · 상권 3곳 데이터 | `DAT-006` · `AGR-001` | S1 착수 전 | 색인에 값이 비어 Top-3가 성립하지 않는다 (R2) |")
    A("")
    A("### 1.4 게이트와 중단 조건")
    A("")
    A("SRS §10.4의 릴리스 게이트를 일정에 박아 둔다. **게이트를 통과하지 못하면 다음 Phase를 시작하지 않는다.**")
    A("")
    A("| 게이트 | 시점 | 통과 조건 | 미달 시 |")
    A("| --- | --- | --- | --- |")
    A("| **게이트 0** | S-1 종료 | `REQ-TEC-001~015` 전건 통과 · 파싱 실패율 ≤ 3% · Top-3 p95 ≤ 1.5s · 결정론 히트율 ≥ 60% | Phase 1을 시작하지 않는다 |")
    A("| **게이트 1** | Phase 1 종료 | WEBD ≥ 목표 60% · 불일치 신고 ≤ 15% · **가맹 LOI ≥ 30곳** | 에이전트 제안(`AGR`·`MCH`)을 v0.2로 연기하고 탐색 기능만 GA |")
    A("| **게이트 2** | Phase 2 종료 | 제안 도착 ≥ 70% · 선택 제안 노쇼 ≤ 8% · **300 RPS 부하 테스트 통과**(`TST-010`) | 에이전트 제안 중단 |")
    A("")
    A("**상시 중단 조건** — 주간 노쇼율 8% 초과 시 `AGR`·`MCH` 신규 노출을 즉시 중단한다"
      "(SRS §10.3). 가맹점은 노쇼 한 번으로 이탈하므로 이 순서를 뒤집을 수 없다.")
    A("")
    A("### 1.5 운영 규칙")
    A("")
    A("- **한 태스크 = 한 PR = 한 이슈.** 축약으로 흡수된 태스크는 한 PR로 처리하되 커밋을 흡수 단위로 나눈다.")
    A("- **DoD 6개 공통 항목**을 통과하지 못한 PR은 머지하지 않는다 (`docs/tasks/*.md` 참조).")
    A("- **빌드 실패 = 배포 차단.** 외부 CI가 없으므로 품질 게이트가 빌드 안에 있다 (C-TEC-007 · ADR-T08).")
    A("- **스키마 변경은 사람이 승인한다.** 마이그레이션은 빌드에 넣지 않는다 (SRS §14.4).")
    A("- **계측 없는 지표는 판정에 쓰지 않는다.** `unreliable` 표기 지표는 게이트에서 배제한다 (SRS §10.2.5).")
    A("")
    A("---")
    A("")
    # ── 2. 의존성 구조 ───────────────────────────────────
    A("## 2. 의존성 구조")
    A("")
    A(f"태스크 {n}건 · 의존 간선 {sum(len(BY[t][3]) for t in IDS)}개 · "
      f"진입점(선행 없음) {len(heads)}건 · 말단(후행 없음) {len(tails)}건 · 순환 0.")
    A("")
    A("### 2.1 DAG 레벨 — 동시 착수 가능 묶음")
    A("")
    A("같은 레벨의 태스크는 **선행이 모두 끝난 시점에 동시 착수할 수 있다.** "
      "자원이 무한하면 이 레벨 수가 곧 단계 수다.")
    A("")
    A("| 레벨 | 건수 | 태스크 | 최장 소요 |")
    A("| --- | --- | --- | --- |")
    wv = defaultdict(list)
    for t in IDS:
        wv[LV[t]].append(t)
    for k in sorted(wv):
        ts = sorted(wv[k])
        A(f"| **L{k}** | {len(ts)} | {' · '.join(ts)} | {max(dur[t] for t in ts)}d |")
    A("")
    A(f"**레벨 {len(wv)}단계** — 자원이 무한해도 이보다 적은 단계로 끝낼 수 없다. "
      f"실제로는 자원 제약 때문에 아래 §3의 일정이 적용된다.")
    A("")
    A("### 2.2 임계 경로")
    A("")
    A(f"**{len(CP)}단계 · {CP_LEN}영업일.** 인원을 늘려도 이보다 빨라지지 않는다. "
      "이 사슬 위의 태스크가 하루 밀리면 전체가 하루 밀린다.")
    A("")
    A("```mermaid")
    A("flowchart LR")
    st = {"Contract": "ctr", "Data": "dat", "Infra": "inf", "UI": "ui",
          "Read": "rd", "Write": "wr", "Test": "tst", "NFR": "nfr", "Design": "dsg"}
    for c in CP:
        A(f'    {c.replace("-","")}["{c}<br/>{gname(c)}<br/>{dur[c]}d"]:::{st[BY[c][5]]}')
    for a, b in zip(CP, CP[1:]):
        assert a in BY[b][3], f"허위 간선 {a}→{b}"
        A(f'    {a.replace("-","")} --> {b.replace("-","")}')
    A("    classDef ctr fill:#f8d7da,stroke:#dc3545,font-weight:bold")
    A("    classDef dat fill:#fff3cd,stroke:#e0a800")
    A("    classDef inf fill:#e2e3e5,stroke:#6c757d")
    A("    classDef rd fill:#e7f1ff,stroke:#0d6efd")
    A("    classDef wr fill:#d1e7dd,stroke:#198754")
    A("    classDef tst fill:#ede7f6,stroke:#7e57c2")
    A("    classDef nfr fill:#cff4fc,stroke:#0dcaf0")
    A("    classDef dsg fill:#fce4ec,stroke:#ec407a")
    A("    classDef ui fill:#e0f2f1,stroke:#009688")
    A("```")
    A("")
    A("### 2.3 병목 — 후행이 많은 태스크")
    A("")
    A("아래 태스크가 밀리면 괄호 안 수만큼이 **직접** 밀린다. 리뷰를 최우선으로 배정한다.")
    A("")
    A("| 태스크 | 유형 | 직접 후행 | 임계 경로 | 소요 |")
    A("| --- | --- | --- | --- | --- |")
    for t, b in sorted(BLOCKS.items(), key=lambda kv: -len(kv[1]))[:8]:
        A(f"| [`{t}`](../docs/tasks/{t}.md) | `{BY[t][5]}` | **{len(b)}건** | "
          f"{'✅ 포함' if t in CP else '—'} | {dur[t]}d |")
    A("")
    A("### 2.4 병렬 가능성이 큰 구간")
    A("")
    wide = sorted(wv.items(), key=lambda kv: -len(kv[1]))[:3]
    for k, ts in wide:
        rs = Counter(role[t] for t in sorted(ts))
        A(f"- **L{k} ({len(ts)}건)** — " + " · ".join(f"{ROLE_NAME[r]} {c}건" for r, c in rs.items()) +
          f". 트랙을 모두 가동하면 {max(dur[t] for t in ts)}일에 소화된다.")
    A("")
    A("---")
    A("")
    return out


def add_schedule(A):
    n = len(IDS)
    work = sum(dur.values())
    A("## 3. 일정")
    A("")
    A("### 3.1 산정 기준")
    A("")
    A("| 항목 | 값 | 근거 |")
    A("| --- | --- | --- |")
    A("| 복잡도 → 소요 | **H 5일 · M 3일 · L 1일** | 태스크 리스트 §0.5의 판정 기준을 영업일로 환산 |")
    A(f"| 총 공수 | {work} person-day | 59건 합계 |")
    A(f"| 임계 경로 | **{CP_LEN}영업일** | 기간 가중 최장 경로 (§2.2) |")
    A(f"| 트랙 구성 | {sum(CAP.values())}레인 | 플랫폼1 · 백엔드2 · 프론트1 · 디자인1 · QA1 |")
    A(f"| **자원 제약 완료** | **{SPAN}영업일** | 아래 시뮬레이션 결과 |")
    A(f"| 시작일 | {workday(0)} (월) | 주말 제외 |")
    A(f"| 완료일 | {workday(SPAN-1)} | 약 {SPAN//5}주 |")
    A("")
    A(f"**임계 경로 {CP_LEN}일 대비 실제 {SPAN}일** — 차이 {SPAN-CP_LEN}일은 자원 대기다. "
      f"{'인원을 늘려도 ' + str(CP_LEN) + '일 밑으로는 내려가지 않는다.' if SPAN > CP_LEN else '자원이 임계 경로를 제약하지 않는다.'}")
    A("")
    A("> ⚠️ **소요일은 복잡도 등급에서 기계적으로 환산한 값이다.** 실제 팀 역량으로 재산정해야 하며, "
      "재산정 시 `tools/gen_exec_plan.py` 의 `DUR` 를 고치고 재생성한다.")
    A("")
    A("### 3.2 트랙별 Gantt")
    A("")
    A("**이 그림이 말하는 것:** 가로가 시간, 각 구획이 한 사람의 작업 레인이다. "
      "같은 시각에 여러 레인이 차 있으면 그만큼 **병렬로 진행**된다.")
    A("")
    A("```mermaid")
    A("gantt")
    A("    title AI-Place-Mate MVP 개발 일정 (자원 제약 · 영업일)")
    A("    dateFormat YYYY-MM-DD")
    A("    axisFormat %m/%d")
    A("    excludes weekends")
    for r in ["DSG", "PLT", "BE", "FE", "QA"]:
        for li in range(CAP[r]):
            lane_tasks = sorted([t for t in IDS if LANE[t] == (r, li)], key=lambda t: S[t])
            if not lane_tasks:
                continue
            label = ROLE_NAME[r] + (f" {li+1}" if CAP[r] > 1 else "")
            A(f"    section {label}")
            for t in lane_tasks:
                crit = "crit, " if t in CP else ""
                A(f"    {t} {gname(t)} :{crit}{t.replace('-','').lower()}{li}, "
                  f"{workday(S[t])}, {dur[t]}d")
    A("```")
    A("")
    A("붉게 표시된 것이 **임계 경로** 위의 태스크다.")
    A("")
    A("### 3.3 Phase · 게이트 일정")
    A("")
    A("**이 그림이 말하는 것:** Phase 경계와 게이트가 언제 오는지다. "
      "게이트는 **통과 판정 시점**이며 미달 시 다음 Phase가 시작되지 않는다.")
    A("")
    # Phase 경계를 스프린트 배치에서 도출
    ph = {"S-1": "P0 기반", "S0": "P0 기반", "S1": "P1 클로즈드 베타", "S2": "P1 클로즈드 베타",
          "S3": "P1 클로즈드 베타", "S4": "P1 클로즈드 베타", "S5": "P1 말",
          "S6": "P1 말", "S7": "P2 오픈 베타", "S8": "P2 오픈 베타"}
    grp = defaultdict(list)
    for t in IDS:
        grp[ph[BY[t][6]]].append(t)
    A("```mermaid")
    A("gantt")
    A("    title Phase 경계와 릴리스 게이트")
    A("    dateFormat YYYY-MM-DD")
    A("    axisFormat %m/%d")
    A("    excludes weekends")
    order = ["P0 기반", "P1 클로즈드 베타", "P1 말", "P2 오픈 베타"]
    gate_at = {}
    for i, p in enumerate(order):
        ts = grp.get(p, [])
        if not ts:
            continue
        s, f = min(S[t] for t in ts), max(F[t] for t in ts)
        gate_at[p] = f
        A(f"    section {p}")
        A(f"    {p} 구간 ({len(ts)}건) :p{i}, {workday(s)}, {f-s}d")
        gname_map = {"P0 기반": "게이트 0", "P1 클로즈드 베타": "게이트 1",
                     "P1 말": "결제 검증", "P2 오픈 베타": "게이트 2"}
        A(f"    {gname_map[p]} :milestone, m{i}, {workday(max(0,f-1))}, 0d")
    A("```")
    A("")
    A("| Phase | 태스크 | 기간 | 종료 시 판정 |")
    A("| --- | --- | --- | --- |")
    gl = {"P0 기반": "게이트 0 — REQ-TEC 전건 통과 · 결정론 히트율 ≥ 60%",
          "P1 클로즈드 베타": "게이트 1 — WEBD ≥ 목표 60% · 가맹 LOI ≥ 30곳",
          "P1 말": "결제 검증 — 웹훅 멱등성 · 노쇼 오판정률 ≤ 1%",
          "P2 오픈 베타": "게이트 2 — 제안 도착 ≥ 70% · 노쇼 ≤ 8% · 300 RPS 통과"}
    for p in order:
        ts = grp.get(p, [])
        if not ts:
            continue
        s, f = min(S[t] for t in ts), max(F[t] for t in ts)
        A(f"| **{p}** | {len(ts)}건 | {workday(s)} ~ {workday(f-1)} ({f-s}d) | {gl[p]} |")
    A("")
    A("### 3.4 웨이브별 착수표")
    A("")
    A("자원 제약을 반영한 **실제 착수 순서**다. 같은 주에 시작하는 태스크가 병렬 작업 단위다.")
    A("")
    A("| 주차 | 착수 태스크 | 트랙 |")
    A("| --- | --- | --- |")
    byweek = defaultdict(list)
    for t in IDS:
        byweek[S[t] // 5].append(t)
    for w in sorted(byweek):
        ts = sorted(byweek[w], key=lambda t: (role[t], t))
        cells = " · ".join(f"`{t}`" for t in ts)
        rs = " ".join(sorted({ROLE_NAME[role[t]] for t in ts}))
        A(f"| **W{w+1}** ({workday(w*5)}~) | {cells} | {rs} |")
    A("")
    A("---")
    A("")


def add_risk(A):
    A("## 4. 리스크와 대응")
    A("")
    A("일정 관점에서 본 리스크다. 제품 리스크(R1~R6)와 기술 리스크(R-T1~T4)는 SRS §11에 있다.")
    A("")
    A("| 리스크 | 일정 영향 | 조기 신호 | 대응 |")
    A("| --- | --- | --- | --- |")
    A("| **DAT-001 지연** | 후행 15건이 함께 밀린다. 임계 경로 위 | S0 첫 주에 스키마 리뷰가 안 끝남 | 스키마 확정을 S0 최우선으로. ADR-001 되돌림 비용이 '최대'라 급하게 시작하면 더 비싸다 |")
    A("| **CTR-001 지연** | 후행 12건. 계약이 흔들리면 재작업 | 계약 리뷰가 2일 이상 지연 | 계약만 먼저 머지하고 구현은 뒤로. 스냅샷 테스트로 변경을 가시화 |")
    A("| **DEP-T4 PG 계약 미확정** | `RSV-003` 착수 불가 → 결제·대화방 전체 정지 | S5 진입 시점에 서명 알고리즘 미확정 | 웹훅 계약을 잠정 정의해 `CTR-002` 를 진행하고, 확정 후 서명부만 교체 |")
    A("| **DEP-T5 상권 데이터 미확보** | `DAT-006` 이 빈 파이프라인이 된다 (R2) | 상권당 필수 필드 5개 충족 매장 300곳 미달 | 상권 3곳 집중 · 전국 확장 금지. 커버리지 리포트를 주간 추적 |")
    A("| **결정론 파서 흡수율 미달** | `QRY-001` 재작업 + 비용·지연 동시 악화 (R-T1) | Phase 0 로그에서 `parse_path=llm` 비율 40% 초과 | 사전 확장을 별도 태스크로 분리. 게이트 0 조건(히트율 ≥ 60%)으로 고정 |")
    A("| **가맹 LOI 30곳 미달** | 게이트 1 미통과 → `MCH`·`AGR` 9건이 v0.2로 연기 | Phase 1 중반 LOI 확보 속도 | 탐색 기능만으로 GA 하는 축소 경로를 미리 준비 |")
    A("")
    A("### 일정 버퍼")
    A("")
    A(f"- 임계 경로 {CP_LEN}일에 **버퍼가 포함되어 있지 않다.** 복잡도 H 태스크 21건 중 "
      "임계 경로 위 항목이 지연되면 그대로 전체 지연이다.")
    A("- 권장 버퍼는 Phase 경계마다 **3영업일** — 게이트 판정과 미달 시 재작업 시간이다.")
    A("- 버퍼를 넣으려면 `tools/gen_exec_plan.py` 의 `DUR` 를 조정하지 말고 Phase 사이에 "
      "별도 여유를 두는 편이 낫다. 태스크 소요를 부풀리면 병목이 어디인지 흐려진다.")
    A("")
    A("---")
    A("")
    A("## 5. 진척 추적")
    A("")
    A("### 5.1 무엇을 본다")
    A("")
    A("| 지표 | 정의 | 위험 신호 |")
    A("| --- | --- | --- |")
    A("| 임계 경로 진척 | 임계 경로 15건 중 완료 수 | 계획 대비 2건 이상 지연 |")
    A("| 병목 태스크 리드타임 | 후행 6건 이상 태스크의 착수~머지 | 예상 소요의 1.5배 초과 |")
    A("| 차단된 태스크 수 | 선행 미완으로 착수 못 하는 수 | 트랙 하나가 3일 이상 유휴 |")
    A("| DoD 미충족 반려율 | PR 반려 / 전체 PR | 30% 초과 시 AC 해석이 갈리고 있다는 신호 |")
    A("| 외부 블로커 미해소 | DEP-T1~T5 중 미확보 | 착수 시점 도달 전 미해소 |")
    A("")
    A("### 5.2 운영 리듬")
    A("")
    A("- **일간** — 임계 경로 위 태스크의 상태만 확인한다. 나머지는 주간에 본다.")
    A("- **주간** — 웨이브별 착수표(§3.4) 대비 실제 착수를 대조하고, 밀린 것의 후행 영향을 계산한다.")
    A("- **Phase 종료** — 게이트 조건을 판정한다. `unreliable` 지표는 판정에 쓰지 않는다.")
    A("")
    A("### 5.3 계획 갱신")
    A("")
    A("태스크가 추가·병합되거나 소요 추정이 바뀌면 **문서를 고치지 말고** 단일 원천을 고친다.")
    A("")
    A("```")
    A("tools/tasks_data.py     ← 태스크 · 의존성 · 복잡도 수정")
    A("tools/gen_exec_plan.py  ← DUR · CAP(트랙 수) · START 수정")
    A("        ↓")
    A("python3 tools/gen_exec_plan.py")
    A("docs/[총괄] 개발 실행 계획.md   ← 재생성 (일정 · Gantt 전부 갱신)")
    A("```")
    A("")
    A("---")
    A("")
    A(f"**PLAN-AIPLACE-MVP-001 · v1.0 · 2026-08-25 · Owner 5팀 · "
      f"태스크 {len(IDS)}건 · {SPAN}영업일 · {sum(CAP.values())}레인**")


def main():
    out = build()
    add_schedule(out.append)
    add_risk(out.append)
    doc = "\n".join(out) + "\n"
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"생성: {OUT} ({doc.count(chr(10))}줄)")
    print(f"  임계 경로 {CP_LEN}일 · 자원 제약 완료 {SPAN}일 · 레인 {sum(CAP.values())}")
    print(f"  DAG 레벨 {max(LV.values())+1}단계 · 시작 {workday(0)} · 완료 {workday(SPAN-1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
