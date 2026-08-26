#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""태스크 리스트 문서 생성기.

`tools/tasks_data.py` 를 단일 원천으로 삼아 문서를 생성한다.
`Blocks`(후행)는 `deps` 에서 역산하므로 수기 작성으로 인한 불일치가 발생하지 않는다.

사용법:
    python3 tools/gen_task_list.py           # 생성 + 검증
    python3 tools/gen_task_list.py --check   # 검증만 (기존 문서와 비교)
"""
import sys, os, re
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tasks_data as D  # noqa: E402

OUT = "docs/plan-docs/[TaskList]AI-Place-Mate-Task-List.md"
BY = {t[0]: t for t in D.TASKS}
IDS = list(BY)


# ── 파생 ──────────────────────────────────────────────────────────────
def blocks_map():
    """deps 역산 — 각 태스크를 선행으로 삼는 후행 태스크 목록."""
    b = defaultdict(list)
    for tid, _, _, deps, _, _, _ in D.TASKS:
        for d in deps:
            b[d].append(tid)
    return {k: sorted(v) for k, v in b.items()}


BLOCKS = blocks_map()

SRS_TEC = "docs/tech-design-docs/[SRS]AI-Place-Mate-SRS-v1_0.md"

# 담당 태스크가 없는 요구사항의 사유 — 근거 없이 비워 두지 않는다
UNCOVERED_REASON = {
    "REQ-FUNC-010": "v0.1은 **스키마 필드만** 확보한다. 필드는 DAT-001에 포함되고 값 적재는 범위 밖 (SRS §14.3)",
}


def srs_defined_reqs():
    """SRS가 앵커로 정의한 요구사항 집합. 파일이 없으면 빈 집합."""
    if not os.path.exists(SRS_TEC):
        return set()
    txt = open(SRS_TEC, encoding="utf-8").read()
    return set(re.findall(r'<a id="(REQ-(?:FUNC|NF|TEC)-\d+[ab]?)"', txt))


def short_label(text, limit=20):
    """mermaid 노드용 축약 — 단어 경계에서 자르고 백틱을 제거한다."""
    t = text.replace("`", "").replace('"', "")
    if len(t) <= limit:
        return t
    cut = t[:limit]
    for sep in (" · ", " — ", " 및 ", " "):
        i = cut.rfind(sep)
        if i > limit * 0.5:
            cut = cut[:i]
            break
    else:
        cut = cut.rstrip()
    # 여는 괄호만 남으면 그 앞에서 자른다 — 읽다 만 느낌을 없앤다
    while cut.count("(") > cut.count(")"):
        cut = cut[:cut.rfind("(")].rstrip()
    return cut + "…"


def longest_path():
    """실제 deps DAG에서 최장 경로를 구한다. 그리지 않은 간선을 그리지 않기 위함."""
    depth, prev = {}, {}
    def d(n):
        if n in depth:
            return depth[n]
        depth[n] = 0
        for m in BY[n][3]:
            if m in BY:
                v = d(m) + 1
                if v > depth[n]:
                    depth[n], prev[n] = v, m
        return depth[n]
    for n in IDS:
        d(n)
    end = max(IDS, key=lambda n: (depth[n], -len(BLOCKS.get(n, []))))
    chain = [end]
    while chain[-1] in prev:
        chain.append(prev[chain[-1]])
    return list(reversed(chain))


def reqs_of(refs):
    """원자 참조 목록에서 요구사항 ID를 뽑는다. 문자열을 쪼개지 않으므로 파편이 생기지 않는다."""
    out = []
    for r in refs:
        out += re.findall(r"REQ-(?:FUNC|NF|TEC)-\d+[ab]?", r)
    return out


def _refkey(r):
    m = re.match(r"^§([\d.]+)(?:-(\d+))?", r)
    if not m:
        return (9, (), r)
    nums = tuple(int(x) for x in m.group(1).split("."))
    return (0, nums + (int(m.group(2)) if m.group(2) else 0,), r)


def render_refs(refs):
    """절 단위로 묶어 렌더한다. 같은 절·같은 ID 접두어가 여럿이면 중괄호로 묶는다.

    예) ['§4.3 REQ-TEC-001', '§4.3 REQ-TEC-003'] → '§4.3 REQ-TEC-{001, 003}'
    """
    groups = []                      # [(키, 라벨목록)] — 입력 순서 유지
    index = {}
    for r in sorted(refs, key=_refkey):
        m = re.match(r"^(§[\d.]+(?:-\d+)?)\s*(.*)$", r)
        key, rest = (m.group(1), m.group(2).strip()) if m else ("", r)
        if key not in index:
            index[key] = len(groups)
            groups.append((key, []))
        if rest:
            groups[index[key]][1].append(rest)
    out = []
    for key, items in groups:
        if not items:
            out.append(key)
            continue
        # 같은 ID 접두어끼리 묶기
        runs, order = {}, []
        for it in items:
            m = re.match(r"^([A-Z][A-Za-z]*(?:-[A-Z]+)*)-(\d+[ab]?)$", it)
            pk = m.group(1) if m else it
            if pk not in runs:
                runs[pk] = []
                order.append(pk)
            runs[pk].append(m.group(2) if m else None)
        parts = []
        for pk in order:
            nums = [n for n in runs[pk] if n]
            if not nums:
                parts.append(pk)
            elif len(nums) == 1:
                parts.append(f"{pk}-{nums[0]}")
            else:
                parts.append(pk + "-{" + ", ".join(nums) + "}")
        out.append((key + " " if key else "") + " · ".join(parts))
    return " · ".join(out)


# ── 검증 ──────────────────────────────────────────────────────────────
def validate():
    errs = []
    if len(set(IDS)) != len(IDS):
        errs.append("중복 태스크 ID 존재")
    for tid, _, refs, deps, cx, ty, sp in D.TASKS:
        for d in deps:
            if d not in BY:
                errs.append(f"{tid}: 미정의 선행 태스크 {d}")
        if cx not in ("H", "M", "L"):
            errs.append(f"{tid}: 잘못된 복잡도 {cx}")
        if ty not in ("Contract", "Data", "Read", "Write", "UI", "Test", "Infra", "NFR", "Design"):
            errs.append(f"{tid}: 잘못된 유형 {ty}")
        if sp not in D.SPRINT_ORDER:
            errs.append(f"{tid}: 잘못된 스프린트 {sp}")
        if not refs:
            errs.append(f"{tid}: SRS 참조 미기재")
        for r in refs:
            if re.fullmatch(r"\d{1,3}[ab]?", r):
                errs.append(f"{tid}: 파편 참조 '{r}' — 절과 ID가 함께 있어야 한다")
    # 순환
    state = {}
    def dfs(n, path):
        if state.get(n) == 1:
            errs.append("순환 의존성: " + " → ".join(path[path.index(n):] + [n]))
            return
        if state.get(n) == 2:
            return
        state[n] = 1
        for m in BY[n][3]:
            if m in BY:
                dfs(m, path + [n])
        state[n] = 2
    for n in IDS:
        dfs(n, [])
    # 스프린트 순서 위반 (선행이 뒤 스프린트에 있으면 안 됨)
    si = {s: i for i, s in enumerate(D.SPRINT_ORDER)}
    for tid, _, _, deps, _, _, sp in D.TASKS:
        for d in deps:
            if d in BY and si[BY[d][6]] > si[sp]:
                errs.append(f"스프린트 역전: {tid}({sp}) ← {d}({BY[d][6]})")
    return errs


# ── 렌더 ──────────────────────────────────────────────────────────────
HDR = ("| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 참조 | "
       "선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |")
SEP = "|---|---|---|---|---|---|---|---|"


def row(t):
    tid, feature, refs, deps, cx, ty, _ = t
    epic = D.EPIC_NAME[tid.split("-")[0]]
    dep = " · ".join(deps) if deps else "None"
    blk = " · ".join(BLOCKS.get(tid, [])) or "None"
    anchor = f'<a id="{tid}"></a>'
    return f"| {anchor}**{tid}** | {epic} | {feature} | `{ty}` | {render_refs(refs)} | {dep} | {blk} | {cx} |"


def epic_table(prefix):
    ts = [t for t in D.TASKS if t[0].startswith(prefix + "-")]
    out = []
    if prefix in D.EPIC_NOTE:
        out += [D.EPIC_NOTE[prefix], ""]
    out += [HDR, SEP] + [row(t) for t in ts] + [""]
    return out


def build():
    L = []
    A = L.append
    n = len(D.TASKS)
    steps = {"Contract": "Step 1", "Data": "Step 1", "Read": "Step 2", "Write": "Step 2",
             "UI": "Step 2", "Test": "Step 3", "Infra": "Step 4", "NFR": "Step 4", "Design": "—"}

    A("# [태스크 리스트] AI-Place-Mate")
    A("")
    A("**문서 ID:** TASK-AIPLACE-MVP-001")
    A("")
    A("**개정 버전:** 3.2 (축약 56건 + 미담당 요구사항 3건 승격 = 59건)")
    A("")
    A("**날짜:** 2026-08-25")
    A("")
    A("**근거 문서:** SRS-AIPLACE-TEC-001 v1.0 (`[SRS]AI-Place-Mate-SRS-v1_0.md`)")
    A("")
    A("**참조 문서:** SRS-AIPLACE-MVP-001 (기술 중립판) · SDD-AIPLACE-MVP-001 (설계 문서) · "
      "ANL-AIPLACE-TASK-001 (방법론 적합성 평가) · ANL-AIPLACE-TASK-002 (축약 검토 — 본 개정의 근거)")
    A("")
    A("> ⚙️ **이 문서는 생성물이다.** 단일 원천은 `tools/tasks_data.py` 이며 "
      "`python3 tools/gen_task_list.py` 로 재생성한다. **직접 편집하지 말 것** — "
      "`후행 태스크(Blocks)` 는 `선행 태스크` 에서 자동 역산되므로 수기 편집은 반드시 불일치를 만든다.")
    A("")
    A("---")
    A("")
    A("## 0. 이 문서를 읽는 법")
    A("")
    A("### 0.1 근거와 범위")
    A("")
    A("본 태스크 리스트는 **기술제약 반영판 SRS**를 기준으로 작성했다. 기술 중립판이 아니라 반영판을 "
      "택한 이유는, 반영판만이 구현 단위(Server Action · Route Handler · RSC · Cron)를 확정하고 있어 "
      "**실행 가능한 태스크로 분해할 수 있기 때문**이다.")
    A("")
    A("- SRS에 **명시되지 않은 기능은 추가하지 않았다.** 모든 태스크는 `관련 SRS 참조` 열로 원문을 지목한다.")
    A("- 요구사항 ID는 두 SRS가 공유하므로, `REQ-FUNC-006` 같은 참조는 양쪽에서 동일하게 성립한다.")
    A("- 연기 대상(SRS §14.3)은 **태스크로 만들지 않았다.** 제외 내역은 부록 D에 있다.")
    A("")
    A("> **참조 표기 규칙** — `관련 SRS 참조` 열의 `§` 는 **기술제약 반영판**의 절이다. "
      "기술 중립판을 가리킬 때만 `중립판 §9.1` 처럼 명시한다. "
      "같은 절의 ID가 여럿이면 `§4.3 REQ-TEC-{001, 003}` 처럼 중괄호로 묶는다.")
    A("")
    A("### 0.2 관점 분리")
    A("")
    A("| Part | 관점 | ID 접두어 | 산출물 성격 |")
    A("| --- | --- | --- | --- |")
    A("| **Part A** | 백엔드 · 프론트엔드 개발 및 인프라 구성 | " +
      " ".join(f"`{p}`" for p in D.PART_A_ORDER) + " | 동작하는 코드 · 구성 |")
    A("| **Part B** | UI/UX 디자인 | `UX` | 화면 정의 · 디자인 산출물 |")
    A("")
    ui_n = sum(1 for t in D.TASKS if t[5] == "UI")
    A(f"Part A 안에서도 **UX 구현({ui_n}건 · 유형 `UI`)과 기능 구현(BE)을 분리**한다. "
      "담당자와 리뷰 관점이 다르고, UX 구현 진척을 독립적으로 추적해야 하기 때문이다. "
      "병합 시에도 두 계층을 섞지 않는다(원칙 P6 · ANL-AIPLACE-TASK-002 §4.4).")
    A("")
    A("### 0.3 유형(Type) 분류")
    A("")
    A("`유형` 열은 태스크가 추출 방법론의 어느 단계에 속하는지를 나타낸다. Read/Write 구분은 "
      "SRS §6.1의 구현 단위(RSC 조회 = Read / Server Action · Cron · 웹훅 = Write)를 따르고, "
      "**화면·클라이언트 코드를 직접 만드는 태스크는 `UI` 로 분리**한다(병합 원칙 P6).")
    A("")
    A("> **Epic과 유형은 서로 다른 축이다.** Epic은 *어느 도메인인가*, 유형은 *어떤 성격의 작업인가* "
      "를 뜻하므로 `INF-002`(Platform & Infra / `UI`)처럼 둘이 어긋나 보이는 조합이 정상이다. "
      "담당자 배정은 **유형**을, 기능 묶음은 **Epic**을 기준으로 본다.")
    A("")
    A("| 유형 | 의미 | 방법론 단계 | 건수 |")
    A("| --- | --- | --- | --- |")
    meaning = {
        "Contract": "DTO · 스키마 · 에러 코드 등 공유 계약",
        "Data": "DB 스키마 · 정규화 사전 · Mock 픽스처",
        "Read": "조회 · 질의 경로 (상태 변경 없음)",
        "Write": "상태 변경 · Server Action · Cron · 웹훅",
        "UI": "**프론트엔드 화면·클라이언트 구현** — 기능 구현(BE)과 분리",
        "Test": "AC를 실행 가능한 테스트로 변환",
        "Infra": "프레임워크 · 배포 · 게이트 · 외부 연동 배선",
        "NFR": "보안 · 관측 · 비용 · 복구",
        "Design": "디자인 토큰 · 화면 정의",
    }
    cnt = defaultdict(int)
    for t in D.TASKS:
        cnt[t[5]] += 1
    for k in ["Contract", "Data", "Read", "Write", "UI", "Test", "Infra", "NFR", "Design"]:
        A(f"| `{k}` | {meaning[k]} | {steps[k]} | {cnt[k]} |")
    A(f"| | | **합계** | **{n}** |")
    A("")
    A("### 0.4 Epic 목록")
    A("")
    A("| Epic | 도메인 | 태스크 수 |")
    A("| --- | --- | --- |")
    for p in D.PART_A_ORDER + D.PART_B_ORDER:
        c = sum(1 for t in D.TASKS if t[0].startswith(p + "-"))
        A(f"| `{p}` | {D.EPIC_NAME[p]} | {c} |")
    A(f"| | **합계** | **{n}** |")
    A("")
    A("### 0.5 복잡도 판정 기준")
    A("")
    A("| 등급 | 기준 | 예 |")
    A("| --- | --- | --- |")
    A("| **H** | 외부 시스템 연동, 새 개념 도입, 되돌림 비용이 크거나 SRS가 임계치를 건 항목 | "
      "PG 웹훅 멱등 처리 · 2단 파싱 · RLS 정책 |")
    A("| **M** | 기존 패턴의 조합. 설계는 정해져 있고 구현량이 있음 | Server Action 작성 · Cron 엔드포인트 |")
    A("| **L** | 설정·선언 수준. 판단이 거의 필요 없음 | 환경 변수 등록 · PITR 활성화 |")
    A("")
    hc = sum(1 for t in D.TASKS if t[4] == "H")
    mc = sum(1 for t in D.TASKS if t[4] == "M")
    lc = sum(1 for t in D.TASKS if t[4] == "L")
    A(f"분포: **H {hc} · M {mc} · L {lc}**")
    A("")
    A("---")
    A("")
    A("## Part A. 백엔드 · 프론트엔드 개발 및 인프라 구성")
    A("")
    for p in D.PART_A_ORDER:
        cnt = sum(1 for t in D.TASKS if t[0].startswith(p + "-"))
        A(f"### `{p}` — {D.EPIC_NAME[p]} ({cnt}건)")
        A("")
        L.extend(epic_table(p))
    A("---")
    A("")
    A("## Part B. UI/UX 디자인")
    A("")
    for p in D.PART_B_ORDER:
        L.extend(epic_table(p))
    A("---")
    A("")
    A("## 부록 A. 임계 경로 (Critical Path)")
    A("")
    chain = longest_path()
    A(f"**이 그림이 말하는 것:** 선행 관계를 따라갈 때 **가장 긴 사슬**이다. "
      f"이 {len(chain)}단계가 전체 일정의 하한을 정한다 — 인원을 늘려도 이보다 빨라지지 않는다.")
    A("")
    A("> 간선은 전부 `선행 태스크` 열에 **실재하는 의존성**이며, 최장 경로 계산으로 뽑았다. "
      "노드의 `후행 N건` 은 직접 후행 수(Blocks)다.")
    A("")
    top = sorted(BLOCKS.items(), key=lambda kv: -len(kv[1]))[:10]
    A("```mermaid")
    A("flowchart LR")
    style = {"Contract": "ctr", "Data": "dat", "Infra": "inf", "UI": "ui",
             "Read": "rd", "Write": "wr", "Test": "tst", "NFR": "nfr", "Design": "dsg"}
    for c in chain:
        t = BY[c]
        A(f'    {c.replace("-","")}["{c}<br/>{short_label(t[1])}<br/>후행 '
          f'{len(BLOCKS.get(c,[]))}건"]:::{style[t[5]]}')
    for a, b in zip(chain, chain[1:]):
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
    A("### 후행 태스크가 많은 상위 10건")
    A("")
    A("| 태스크 | Feature | 유형 | 직접 후행 수 | 후행 태스크 |")
    A("| --- | --- | --- | --- | --- |")
    for tid, bl in top:
        t = BY[tid]
        A(f"| [`{tid}`](#{tid}) | {t[1]} | `{t[5]}` | **{len(bl)}** | {' · '.join(bl)} |")
    A("")
    A("---")
    A("")
    A("## 부록 B. 스프린트 배치")
    A("")
    A("SRS §14.2의 스프린트 정의에 태스크를 배치한 것이다. **선행 태스크가 뒤 스프린트에 놓이는 "
      "역전은 생성 시 검증으로 차단된다.**")
    A("")
    A("| 스프린트 | Part A | Part B |")
    A("| --- | --- | --- |")
    for s in D.SPRINT_ORDER:
        a = [t[0] for t in D.TASKS if t[6] == s and not t[0].startswith("UX-")]
        b = [t[0] for t in D.TASKS if t[6] == s and t[0].startswith("UX-")]
        A(f"| **{D.SPRINT_TITLE[s]}** | {' · '.join(a) or '—'} | {' · '.join(b) or '—'} |")
    A("")
    A("**Phase 경계** — S-1 ~ S4가 Phase 1 클로즈드 베타, S5 ~ S6이 Phase 1 말, "
      "S7 ~ S8이 Phase 2다 (SRS §10.4 게이트 조건과 정합).")
    A("")
    A("---")
    A("")
    A("## 부록 C. 요구사항 커버리지")
    A("")
    A("`refs` 원자 참조 목록에서 요구사항 ID를 뽑아 자동 생성한 표다. "
      "문자열을 쪼개지 않으므로 파편으로 인한 누락이 생기지 않는다.")
    A("")
    cov = defaultdict(list)
    for tid, _, refs, _, _, _, _ in D.TASKS:
        for r in reqs_of(refs):
            cov[r].append(tid)
    def key(r):
        m = re.match(r"REQ-(FUNC|NF|TEC)-(\d+)([ab]?)", r)
        return ({"FUNC": 0, "NF": 1, "TEC": 2}[m.group(1)], int(m.group(2)), m.group(3))
    defined = srs_defined_reqs()
    uncovered = sorted(defined - set(cov), key=key) if defined else []
    A("| 요구사항 | 담당 태스크 | 건수 |")
    A("| --- | --- | --- |")
    for r in sorted(cov, key=key):
        A(f"| `{r}` | {' · '.join(sorted(set(cov[r])))} | {len(set(cov[r]))} |")
    A("")
    if defined:
        A(f"SRS(기술제약 반영판)가 정의한 요구사항 **{len(defined)}종** 중 "
          f"**{len(cov)}종**이 담당 태스크를 가진다.")
        A("")
        if uncovered:
            A("**담당 태스크가 없는 요구사항**")
            A("")
            A("| 요구사항 | 사유 |")
            A("| --- | --- |")
            for r in uncovered:
                A(f"| `{r}` | {UNCOVERED_REASON.get(r, '미배정 — 확인 필요')} |")
        else:
            A("**누락 0건** — 정의된 요구사항 전부가 담당 태스크를 가진다.")
    else:
        A(f"자동 추출된 요구사항 **{len(cov)}종**이 담당 태스크를 가진다.")
    A("")
    A("---")
    A("")
    A("## 부록 D. 태스크로 만들지 않은 것")
    A("")
    A("SRS에 언급되지만 **의도적으로 태스크에서 제외**한 항목이다. "
      "임의 추가를 막는 것만큼 임의 누락을 밝히는 것도 필요하다.")
    A("")
    A("| 항목 | 근거 | 사유 |")
    A("| --- | --- | --- |")
    for a, b, c in [
        ("다지점 공정 지점 산출", "§14.3 · §7", "v0.2+ 연기 대상"),
        ("리뷰 3축 재가공", "§14.3 · §7.2", "v0.2+ 연기 대상"),
        ("AI 예약 에이전트", "§14.3", "v0.2+ 연기 대상"),
        ("성분·접근성 데이터 커버리지", "§14.3 · §4.1 REQ-FUNC-010", "v0.1은 **스키마 필드만** — DAT-002에 포함되고 값 적재는 범위 밖"),
        ("광고 상품", "§14.3 · ADR-004", "도입 계획 없음"),
        ("결제·정산 자체 구축", "§14.3 · LIM-01", "PG 위탁"),
        ("지도·경로 API 연동", "§3.2 · LIM-06", "v0.1 미사용"),
        ("실시간 매장 상태 연동", "§3.2 · §7.4 · LIM-07", "제휴 검토 단계 — 단가 조건 미확정"),
        ("마이크로프런트엔드 분리", "§7.3", "단일 앱의 한계가 드러난 이후 검토"),
        ("플랫폼 장애 대응 · 3,000 RPS 달성", "§15.1", "**미해소 항목** — 발주 측 결정 대기 중이라 태스크로 확정할 수 없음"),
    ]:
        A(f"| {a} | {b} | {c} |")
    A("")
    A("---")
    A("")
    A(f"**TASK-AIPLACE-MVP-001 · v3.2 · 2026-08-25 · Owner 5팀 · 태스크 {n}건**")
    return "\n".join(L) + "\n"


def main():
    errs = validate()
    if errs:
        print("검증 실패:")
        for e in errs:
            print("  ✗", e)
        return 1
    doc = build()
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        same = cur == doc
        print("문서가 데이터와 일치합니다." if same else "문서가 데이터와 다릅니다 — 재생성 필요")
        return 0 if same else 1
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"생성: {OUT} ({doc.count(chr(10))}줄 · 태스크 {len(D.TASKS)}건)")
    print(f"  Blocks 역산: {sum(len(v) for v in BLOCKS.values())}개 관계")
    print("  검증 통과: 중복 0 · 미정의 선행 0 · 순환 0 · 스프린트 역전 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
