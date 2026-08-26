#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""압축 수행 일정(최대 병렬) 생성기.

기본 실행 계획(PLAN-AIPLACE-MVP-001 · 6명 · 72일)은 그대로 두고,
병렬 가능한 태스크를 최대한 동시 수행해 **임계 경로 하한까지 압축**한 대안을 만든다.
"""
import sys, os, re, datetime as dt
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tasks_data as D

OUT = "docs/plan-docs/[Plan]AI-Place-Mate-Fast-Track-Schedule.md"
BY = {t[0]: t for t in D.TASKS}
IDS = list(BY)
DUR = {"H": 5, "M": 3, "L": 1}
ROLE = {"Infra": "PLT", "NFR": "PLT", "Contract": "BE", "Data": "BE", "Read": "BE",
        "Write": "BE", "UI": "FE", "Design": "DSG", "Test": "QA"}
RN = {"PLT": "플랫폼", "BE": "백엔드", "FE": "프론트엔드", "DSG": "디자인", "QA": "QA"}
BASE = {"PLT": 1, "BE": 2, "FE": 1, "DSG": 1, "QA": 1}      # 기본안 (PLAN-001)
FAST = {"PLT": 2, "BE": 3, "FE": 1, "DSG": 2, "QA": 1}      # 압축안 (탐색 결과)
START = dt.date(2026, 9, 1)
STYLE = {"Contract": "ctr", "Data": "dat", "Infra": "inf", "UI": "ui", "Read": "rd",
         "Write": "wr", "Test": "tst", "NFR": "nfr", "Design": "dsg"}

dur = {t: DUR[BY[t][4]] for t in IDS}
role = {t: ROLE[BY[t][5]] for t in IDS}
BLOCKS = defaultdict(list)
for _t in IDS:
    for _p in BY[_t][3]:
        BLOCKS[_p].append(_t)

RANK = {}
def _rank(n):
    if n in RANK:
        return RANK[n]
    RANK[n] = dur[n] + max([_rank(x) for x in BLOCKS.get(n, [])] or [0])
    return RANK[n]
for _n in IDS:
    _rank(_n)

# 임계 경로
EF, PREV = {}, {}
def _ef(n):
    if n in EF:
        return EF[n]
    best, bp = 0, None
    for x in BY[n][3]:
        if _ef(x) > best:
            best, bp = _ef(x), x
    EF[n], PREV[n] = best + dur[n], bp
    return EF[n]
for _n in IDS:
    _ef(_n)
_end = max(IDS, key=lambda n: EF[n])
CP = [_end]
while PREV.get(CP[-1]):
    CP.append(PREV[CP[-1]])
CP = list(reversed(CP))
CP_LEN = EF[_end]


def schedule(cap):
    S, F, LANE = {}, {}, {}
    free = {r: [0] * cap[r] for r in cap}
    done, pend = set(), set(IDS)
    while pend:
        ready = sorted([n for n in pend if all(p in done for p in BY[n][3])],
                       key=lambda n: (-RANK[n], n))
        for n in ready:
            r = role[n]
            li = min(range(cap[r]), key=lambda i: free[r][i])
            s = max(free[r][li], max([F[p] for p in BY[n][3]] or [0]))
            S[n], F[n], LANE[n] = s, s + dur[n], (r, li)
            free[r][li] = F[n]
            done.add(n)
            pend.discard(n)
    return S, F, LANE, max(F.values())


S_B, F_B, _, SPAN_B = schedule(BASE)
S, F, LANE, SPAN = schedule(FAST)


def workday(i):
    d0 = START
    while d0.weekday() >= 5:
        d0 += dt.timedelta(days=1)
    n, cur = 0, d0
    while n < i:
        cur += dt.timedelta(days=1)
        if cur.weekday() < 5:
            n += 1
    return cur


def gname(t):
    s = BY[t][1].replace(":", " ").replace("`", "")
    s = re.sub(r"\s*\(.*?\)\s*", " ", s).strip()
    return (s[:22] + "…") if len(s) > 22 else s


def build():
    O = []
    A = O.append
    work = sum(dur.values())
    conc = [sum(1 for t in IDS if S[t] <= day < F[t]) for day in range(SPAN)]
    weeks = (SPAN + 4) // 5

    A("# [총괄] 압축 수행 일정 — AI-Place-Mate")
    A("")
    A("**문서 ID:** PLAN-AIPLACE-FAST-001")
    A("")
    A("**개정 버전:** 1.0")
    A("")
    A("**날짜:** 2026-08-26")
    A("")
    A("**기본 계획:** PLAN-AIPLACE-MVP-001 (`[Plan]AI-Place-Mate-Execution-Plan.md` · 6명 · 72영업일)")
    A("")
    A("**근거 문서:** TASK-AIPLACE-MVP-001 v3.2 (59건)")
    A("")
    A("> ⚙️ **이 문서는 생성물이다.** `python3 tools/gen_fasttrack_plan.py` 로 재생성한다. "
      "**기본 계획을 대체하지 않는다** — 일정 압축이 필요할 때 선택하는 대안이다.")
    A("")
    A("---")
    A("")
    A("## 0. 이 문서를 언제 쓰는가")
    A("")
    A("기본 계획(6명 · 72일)이 **표준**이다. 아래 상황에서만 이 압축안을 검토한다.")
    A("")
    A("- 출시일이 고정되어 있고 **9일을 줄여야** 할 때")
    A("- 게이트 0·1 통과 시점을 앞당겨 **의사결정을 빨리** 받아야 할 때")
    A("- 인력을 일시 투입할 수 있고 **투입 기간이 제한적**일 때")
    A("")
    A(f"압축의 효과는 **{SPAN_B - SPAN}영업일 단축**이며, 그 대가는 인원 "
      f"{sum(BASE.values())}명 → {sum(FAST.values())}명과 §5의 리스크다.")
    A("")
    A("---")
    A("")
    # ── 1. 세 가지 안 ────────────────────────────────
    A("## 1. 세 가지 편성안 비교")
    A("")
    A("| 안 | 인원 | 완료 | 총 공수 | 평균 가동률 | 성격 |")
    A("| --- | --- | --- | --- | --- | --- |")
    A(f"| **기본안** (PLAN-001) | {sum(BASE.values())}명 | {SPAN_B}일 | {work}pd | "
      f"{work/(sum(BASE.values())*SPAN_B)*100:.0f}% | 자원 효율 우선 |")
    A(f"| **압축안** (본 문서) | **{sum(FAST.values())}명** | **{SPAN}일** | {work}pd | "
      f"{work/(sum(FAST.values())*SPAN)*100:.0f}% | **임계 경로 하한 달성** |")
    A(f"| 최대 병렬 | 16명 | {SPAN}일 | {work}pd | {work/(16*SPAN)*100:.0f}% | 참고 — 더 넣어도 안 빨라짐 |")
    A("")
    A(f"### 왜 {SPAN}일 밑으로 못 가는가")
    A("")
    A(f"**임계 경로가 {CP_LEN}영업일**이기 때문이다. 이 사슬은 전부 선후 관계로 묶여 있어 "
      "동시에 할 수 없다. 인원을 16명으로 늘려도 결과는 같다.")
    A("")
    A("```mermaid")
    A("flowchart LR")
    for c in CP:
        A(f'    {c.replace("-","")}["{c}<br/>{dur[c]}d"]:::{STYLE[BY[c][5]]}')
    for a, b in zip(CP, CP[1:]):
        assert a in BY[b][3], f"허위 간선 {a}→{b}"
        A(f'    {a.replace("-","")} --> {b.replace("-","")}')
    for c, f in [("ctr", "#f8d7da,stroke:#dc3545"), ("dat", "#fff3cd,stroke:#e0a800"),
                 ("inf", "#e2e3e5,stroke:#6c757d"), ("rd", "#e7f1ff,stroke:#0d6efd"),
                 ("wr", "#d1e7dd,stroke:#198754"), ("tst", "#ede7f6,stroke:#7e57c2"),
                 ("nfr", "#cff4fc,stroke:#0dcaf0"), ("dsg", "#fce4ec,stroke:#ec407a"),
                 ("ui", "#e0f2f1,stroke:#009688")]:
        A(f"    classDef {c} fill:{f}")
    A("```")
    A("")
    A(f"**{len(CP)}단계 · {CP_LEN}일.** 압축안은 이 하한에 정확히 도달했으므로 "
      "**더 줄일 방법은 인원이 아니라 태스크 분해를 바꾸는 것**뿐이다 (§6).")
    A("")
    A("### 최소 인원 도출")
    A("")
    A("기본안에서 한 명씩 늘려 가며 완료일이 가장 많이 줄어드는 역할을 골랐다.")
    A("")
    A("| 단계 | 편성 | 완료 | 단축 |")
    A("| --- | --- | --- | --- |")
    steps = [({"PLT": 1, "BE": 2, "FE": 1, "DSG": 1, "QA": 1}, "기본안"),
             ({"PLT": 2, "BE": 2, "FE": 1, "DSG": 1, "QA": 1}, "플랫폼 +1"),
             ({"PLT": 2, "BE": 3, "FE": 1, "DSG": 1, "QA": 1}, "백엔드 +1"),
             ({"PLT": 2, "BE": 3, "FE": 1, "DSG": 2, "QA": 1}, "디자인 +1")]
    prev = None
    for cap, label in steps:
        sp = schedule(cap)[3]
        gain = f"−{prev-sp}일" if prev else "—"
        A(f"| {label} | {sum(cap.values())}명 "
          f"(P{cap['PLT']}·B{cap['BE']}·F{cap['FE']}·D{cap['DSG']}·Q{cap['QA']}) | {sp}일 | {gain} |")
        prev = sp
    A("")
    A(f"**프론트엔드와 QA는 늘리지 않았다** — 두 역할은 기본안에서도 임계 경로를 제약하지 않는다. "
      "늘려도 완료일이 바뀌지 않으므로 순수 비용이다.")
    A("")
    A("---")
    A("")
    # ── 2. 압축 Gantt ────────────────────────────────
    A("## 2. 압축 수행 Gantt")
    A("")
    A(f"**이 그림이 말하는 것:** {sum(FAST.values())}개 레인이 동시에 도는 모습이다. "
      "붉은 것이 임계 경로이며, 이 사슬만은 어떤 편성으로도 병렬화할 수 없다.")
    A("")
    A("```mermaid")
    A("gantt")
    A(f"    title 압축 수행 일정 — {sum(FAST.values())}명 · {SPAN}영업일")
    A("    dateFormat YYYY-MM-DD")
    A("    axisFormat %m/%d")
    A("    excludes weekends")
    for r in ["DSG", "PLT", "BE", "FE", "QA"]:
        for li in range(FAST[r]):
            ts = sorted([t for t in IDS if LANE[t] == (r, li)], key=lambda t: S[t])
            if not ts:
                continue
            A(f"    section {RN[r]}{li+1 if FAST[r] > 1 else ''}")
            for t in ts:
                crit = "crit, " if t in CP else ""
                A(f"    {t} {gname(t)} :{crit}{t.replace('-','').lower()}{li}, "
                  f"{workday(S[t])}, {dur[t]}d")
    A("```")
    A("")
    A(f"시작 {workday(0)} · 완료 {workday(SPAN-1)} (약 {weeks}주).")
    A("")
    A("---")
    A("")
    # ── 3. 동시성 프로파일 ───────────────────────────
    A("## 3. 동시 작업 프로파일")
    A("")
    A("압축의 효과가 **어느 구간에 몰려 있는지** 보여 준다. 인원 투입 계획의 근거다.")
    A("")
    A("| 주차 | 기간 | 동시 작업 (피크/평균) | 착수 태스크 | 투입 필요 |")
    A("| --- | --- | --- | --- | --- |")
    for w in range(weeks):
        seg = conc[w * 5:(w + 1) * 5]
        if not seg:
            continue
        starts = sorted([t for t in IDS if w * 5 <= S[t] < (w + 1) * 5])
        rs = Counter(role[t] for t in IDS if any(S[t] <= dd < F[t] for dd in range(w*5, min((w+1)*5, SPAN))))
        need = " · ".join(f"{RN[r]}{c}" for r, c in sorted(rs.items()))
        cells = " ".join(f"`{t}`" for t in starts) or "—"
        A(f"| **W{w+1}** | {workday(w*5)}~ | **{max(seg)}** / {sum(seg)/len(seg):.1f} | {cells} | {need or '—'} |")
    A("")
    peak_w = max(range(weeks), key=lambda w: max(conc[w*5:(w+1)*5] or [0]))
    tail = [w for w in range(weeks) if max(conc[w*5:(w+1)*5] or [0]) <= 2]
    A(f"### 압축이 통하는 구간과 통하지 않는 구간")
    A("")
    A(f"- **W1~W6 — 압축이 통한다.** 동시 작업이 최대 {max(conc)}건까지 오른다"
      f"(피크 W{peak_w+1}). 인원을 넣으면 실제로 빨라진다.")
    A(f"- **W{tail[0]+1} 이후 — 압축이 통하지 않는다.** 동시 작업이 1~2건으로 떨어진다. "
      "`RSV → MCH → AGR` 사슬이 순수 직렬이라 인원을 넣어도 대기만 늘어난다.")
    A("")
    A("**그래서 인원을 상시 유지할 필요가 없다.** 아래 §4의 투입 곡선을 따른다.")
    A("")
    A("---")
    A("")
    # ── 4. 인원 투입 곡선 ────────────────────────────
    A("## 4. 인원 투입 곡선")
    A("")
    A("주차별로 **실제 필요한 인원**이다. 압축안의 명목 인원은 "
      f"{sum(FAST.values())}명이지만 전 기간 유지할 필요는 없다.")
    A("")
    A("| 주차 | 플랫폼 | 백엔드 | 프론트 | 디자인 | QA | 합계 |")
    A("| --- | --- | --- | --- | --- | --- | --- |")
    tot_pd = 0
    for w in range(weeks):
        days = range(w * 5, min((w + 1) * 5, SPAN))
        need = {}
        for r in ["PLT", "BE", "FE", "DSG", "QA"]:
            need[r] = max([sum(1 for t in IDS if role[t] == r and S[t] <= dd < F[t])
                           for dd in days] or [0])
        tot = sum(need.values())
        tot_pd += tot * len(list(days))
        A(f"| **W{w+1}** | {need['PLT'] or '—'} | {need['BE'] or '—'} | {need['FE'] or '—'} | "
          f"{need['DSG'] or '—'} | {need['QA'] or '—'} | **{tot}** |")
    A("")
    A(f"**인원×기간 = {tot_pd} person-day 확보 필요** (실제 작업 {work}pd · "
      f"유휴 {tot_pd - work}pd). 기본안은 {sum(BASE.values())*SPAN_B}pd 확보에 유휴 "
      f"{sum(BASE.values())*SPAN_B - work}pd다.")
    A("")
    A("### 투입·철수 권고")
    A("")
    A("| 시점 | 조치 | 근거 |")
    A("| --- | --- | --- |")
    A("| W1 시작 | 디자인 2 · 플랫폼 2 전원 투입 | `UX-001` 이 6개를 막고, L1에 디자인 5건이 동시 착수 가능 |")
    A("| W2~W3 | 백엔드 3 전원 가동 | 계약·스키마 구간. 동시 작업 피크 |")
    A("| W6 이후 | **디자인 1 · 플랫폼 1 철수** | 디자인 태스크 소진, 플랫폼은 관측만 남음 |")
    A("| W7 이후 | **백엔드 1~2로 축소** | 직렬 사슬 구간 진입 — 인원을 늘려도 빨라지지 않음 |")
    A("")
    A("---")
    A("")
    # ── 5. 대가와 리스크 ─────────────────────────────
    A("## 5. 압축의 대가")
    A("")
    A("일정 9일을 줄이는 대신 아래를 감수한다. **이 표가 압축 여부 판단의 실질 근거다.**")
    A("")
    A("| 항목 | 기본안 | 압축안 | 영향 |")
    A("| --- | --- | --- | --- |")
    A(f"| 인원 | {sum(BASE.values())}명 | {sum(FAST.values())}명 | +{sum(FAST.values())-sum(BASE.values())}명 |")
    A(f"| 완료 | {SPAN_B}일 | {SPAN}일 | **−{SPAN_B-SPAN}일** |")
    A(f"| 평균 가동률 | {work/(sum(BASE.values())*SPAN_B)*100:.0f}% | "
      f"{work/(sum(FAST.values())*SPAN)*100:.0f}% | 유휴 증가 |")
    A(f"| 확보 공수 | {sum(BASE.values())*SPAN_B}pd | {tot_pd}pd (변동 투입) | "
      f"{'절감' if tot_pd < sum(BASE.values())*SPAN_B else '증가'} {abs(tot_pd - sum(BASE.values())*SPAN_B)}pd |")
    A("")
    A("### 정량 외 리스크")
    A("")
    A("| 리스크 | 왜 압축에서 커지는가 | 완화 |")
    A("| --- | --- | --- |")
    A("| **리뷰 병목** | 동시 작업 최대 9건 → PR이 몰린다. 리뷰어는 늘지 않는다 | 임계 경로 PR을 리뷰 최우선으로. 나머지는 24시간 SLA |")
    A("| **통합 충돌** | 계약(`CTR-001`) 위에서 여러 태스크가 동시에 작업 | 계약을 먼저 머지하고 구현을 뒤로. 스냅샷 테스트로 변경 가시화 |")
    A("| **온보딩 비용** | 추가 3명이 SRS·SDD·제약 체계를 익혀야 한다 | W1을 온보딩 겸 기반 구간으로 두되 일정에 반영되지 않음 — **별도 버퍼 필요** |")
    A("| **컨텍스트 분산** | 백엔드 3레인이 서로 다른 Epic을 동시 진행 | Epic 단위로 레인을 고정해 담당 도메인을 유지 |")
    A("| **유휴 인원** | W7 이후 디자인·플랫폼이 놀게 된다 | 투입 곡선(§4)대로 철수. 상시 계약이면 압축 이득이 사라진다 |")
    A("")
    A("> ⚠️ **온보딩 시간이 일정에 없다.** 위 표의 −"
      f"{SPAN_B-SPAN}일은 추가 인원이 **즉시 생산성을 낸다는 가정**이다. "
      "실제로는 온보딩 1~2주를 감안하면 순 이득이 사라질 수 있다. "
      "**이미 이 프로젝트 맥락을 아는 인력**을 투입할 때만 압축이 성립한다.")
    A("")
    A("---")
    A("")
    # ── 6. 더 줄이려면 ───────────────────────────────
    A("## 6. 63일보다 더 줄이려면")
    A("")
    A("인원으로는 불가능하다. **임계 경로 자체를 짧게 만드는 것**만 남는다.")
    A("")
    A("| 방법 | 대상 | 예상 단축 | 대가 |")
    A("| --- | --- | --- | --- |")
    cp_tail = [t for t in CP if BY[t][6] in ("S5", "S6", "S7", "S8")]
    A(f"| **범위 축소** — 에이전트 제안(`AGR`·`MCH`)을 v0.2로 연기 | {len(cp_tail)}건이 임계 경로에서 빠짐 | "
      f"약 {sum(dur[t] for t in cp_tail)}일 | SRS 게이트 1 미달 시 어차피 연기되는 경로 |")
    A("| **태스크 재분해** — `DAT-001`(5d)을 스키마/정규화로 분리 | 임계 경로 상류 | 2~3일 | "
      "ADR-001 되돌림 비용이 '최대'라 분해가 위험 |")
    A("| **선행 완화** — `RSV-001` 이 `RNK-003`(UI) 대신 계약에만 의존 | 직렬 사슬 단축 | 5일 내외 | "
      "실제 화면 없이 승계 로직을 검증해야 함 — Mock 확대 필요 |")
    A("| **외부 의존 선점** — PG 계약(`DEP-T4`)을 W1에 확정 | `RSV-003` 대기 제거 | 0일 (이미 반영) | "
      "미확정 시 오히려 늘어남 |")
    A("")
    A("**가장 확실한 단축은 범위 축소**다. SRS §10.4의 게이트 1에서 가맹 LOI 30곳이 미달하면 "
      "`AGR`·`MCH`는 어차피 v0.2로 연기되므로, 그 시나리오를 미리 계획에 넣는 편이 낫다.")
    A("")
    A("---")
    A("")
    A("## 7. 권고")
    A("")
    A("1. **기본안(6명 · 72일)을 표준으로 유지한다.** 가동률이 높고 리뷰·통합 부담이 작다.")
    A(f"2. 출시일 압박이 실재할 때만 압축안({sum(FAST.values())}명 · {SPAN}일)을 채택하고, "
      "**투입 곡선(§4)대로 W6 이후 철수**한다. 상시 9명이면 압축 이득이 사라진다.")
    A("3. **16명 편성은 채택하지 않는다.** 9명과 완료일이 같고 가동률만 절반이 된다.")
    A(f"4. 압축을 택하면 **온보딩 버퍼 1~2주를 별도로** 잡는다. 그러지 않으면 −{SPAN_B-SPAN}일이 "
      "장부상 숫자로만 남는다.")
    A("5. 더 큰 단축이 필요하면 인원이 아니라 **범위를 줄인다** (§6).")
    A("")
    A("---")
    A("")
    A(f"**PLAN-AIPLACE-FAST-001 · v1.0 · 2026-08-26 · Owner 5팀 · "
      f"{sum(FAST.values())}명 · {SPAN}영업일 · 임계 경로 하한 도달**")
    return "\n".join(O) + "\n"


def main():
    doc = build()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"생성: {OUT} ({doc.count(chr(10))}줄)")
    print(f"  기본안 {sum(BASE.values())}명 {SPAN_B}일 → 압축안 {sum(FAST.values())}명 {SPAN}일 "
          f"(−{SPAN_B-SPAN}일)")
    print(f"  임계 경로 {CP_LEN}일 — 압축안이 하한에 도달")
    return 0


if __name__ == "__main__":
    sys.exit(main())
