#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""태스크별 GitHub Issue 명세 생성기 (docs/tasks/<ID>.md).

기계적 부분(제목·라벨·References 앵커·의존성·DoD)은 `tasks_data.py` 에서 파생하고,
실질 내용(목적·실행 계획·AC·제약)은 `task_specs.py` 가 제공한다.
템플릿은 `.github/ISSUE_TEMPLATE/feature-task.md` 의 7개 섹션을 그대로 따른다.

사용법:
    python3 tools/gen_task_docs.py           # 전체 생성
    python3 tools/gen_task_docs.py DAT-001   # 특정 태스크만
"""
import sys, os, re
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tasks_data as D
import task_specs as S

OUT = "docs/tasks"
TASK_DOC = "/docs/plan-docs/[TaskList]AI-Place-Mate-Task-List.md"
SRS_TEC = "/docs/tech-design-docs/[SRS]AI-Place-Mate-SRS-v1_0.md"
SRS_NEU = "/docs/tech-design-docs/[SRS]AI-Place-Mate-SRS-v0_1.md"
SDD = "/docs/tech-design-docs/[Diagrams]AI-Place-Mate-Diagrams.md"

BY = {t[0]: t for t in D.TASKS}
BLOCKS = defaultdict(list)
for _t, _f, _r, _deps, _c, _ty, _sp in D.TASKS:
    for _d in _deps:
        BLOCKS[_d].append(_t)

# 데이터 파일 주석에서 흡수 목록 복원 (축약 이력 안내용)
ABSORBED = {}
for line in open(os.path.join(os.path.dirname(__file__), "tasks_data.py"), encoding="utf-8"):
    m = re.match(r'\s*\("([A-Z]{2,3}-\d{3})",', line)
    if m:
        c = re.search(r"#\s*←\s*(.*)$", line)
        if c:
            ABSORBED[m.group(1)] = re.findall(r"[A-Z]{2,3}-\d{3}", c.group(1))

PART = {"Design": "part:design", "UI": "part:frontend",
        "Infra": "part:infra", "NFR": "part:infra", "Test": "part:backend"}


def primary_req(refs):
    for r in refs:
        m = re.search(r"REQ-(?:FUNC|NF|TEC)-\d+[ab]?", r)
        if m:
            return m.group(0)
    return None


def neutral_req(req):
    """중립판에 존재하는 요구사항 ID로 환산. 없으면 None."""
    if not req or req.startswith("REQ-TEC"):
        return None
    return re.sub(r"^(REQ-NF-\d+)[ab]$", r"\1", req)


def render(tid):
    t = BY[tid]
    _, feature, refs, deps, cx, ty, sp = t
    spec = S.SPECS[tid]
    epic = tid.split("-")[0]
    req = primary_req(refs)
    neu = neutral_req(req)
    L = []
    A = L.append

    A("---")
    A("name: GitHub Project 용 TASK 템플릿")
    A("about: SRS 기반의 구체적인 개발 태스크 명세")
    A(f'title: "[Feature] {tid}: {feature}"')
    A(f"labels: 'feature, {PART.get(ty, 'part:backend')}, epic:{epic}, "
      f"complexity:{cx}, sprint:{sp}'")
    A("assignees: ''")
    A("---")
    A("")

    # 🎯 Summary
    A("## 🎯 Summary")
    A(f"- 기능명: [{tid}] {feature}")
    A(f"- 목적: {spec['purpose']}")
    if tid in ABSORBED:
        A(f"- ⚠️ **축약(v3.0)으로 `{'` · `'.join(ABSORBED[tid])}` 를 흡수했다.** "
          "한 PR로 처리하되 커밋은 흡수 단위로 나눈다.")
    A("")

    # 🔗 References
    A("## 🔗 References (Spec & Context)")
    A("> 💡 AI Agent & Dev Note: 작업 시작 전 아래 문서를 반드시 먼저 Read/Evaluate 할 것.")
    A(f"- 태스크 리스트: `{TASK_DOC}#{tid}`")
    tec = f"`{SRS_TEC}#{req}`" if req else f"`{SRS_TEC}`"
    A(f"- SRS 문서(기술제약 반영판): {tec} — {' · '.join(refs)}")
    A(f"- SRS 문서(기술 중립판): `{SRS_NEU}#{neu}`" if neu
      else "- SRS 문서(기술 중립판): 해당 없음 — 기술 제약에서 파생된 요구사항")
    A(f"- 설계 문서(SDD): `{SDD}#{spec['sdd']}`" if spec.get("sdd")
      else f"- 설계 문서(SDD): `{SDD}` — 대응 도면 없음")
    A(f"- 시퀀스 다이어그램: `{spec.get('seq', '해당 없음')}`")
    A(f"- 데이터 모델 (ERD): `{SDD}#31-erd--개체와-관계`")
    A(f"- 서버 진입점 명세: `{SRS_TEC}#61-서버-진입점-목록`")
    for extra in spec.get("refs_extra", []):
        A(f"- {extra}")
    A("")

    # ✅ Task Breakdown
    A("## ✅ Task Breakdown (실행 계획)")
    for b in spec["breakdown"]:
        A(f"- [ ] {b}")
    A("")

    # 🧪 Acceptance Criteria
    A("## 🧪 Acceptance Criteria (BDD/GWT)")
    A("")
    for i, sc in enumerate(spec["scenarios"], 1):
        tag = " (실패 흐름)" if sc.get("fail") else ""
        A(f"Scenario {i}{tag}: {sc['title']}")
        A(f"- Given: {sc['given']}")
        A(f"- When: {sc['when']}")
        then = sc["then"]
        if sc.get("slo"):
            then += f" **{sc['slo']}**"
        A(f"- Then: {then}")
        A("")

    # ⚙️ Constraints
    A("## ⚙️ Technical & Non-Functional Constraints")
    for label, text in spec["constraints"]:
        A(f"- {label}: {text}")
    A("")

    # 🏁 DoD
    A("## 🏁 Definition of Done (DoD)")
    A("- [ ] 모든 Acceptance Criteria를 충족하는가?")
    A("- [ ] 단위 테스트(Unit Test) 및 통합 테스트(Integration Test)가 추가되었고 통과하는가?")
    A("- [ ] 정적 분석 경고가 없는가? <!-- tsc --noEmit · ESLint · verify-constraints.mjs (REQ-TEC-012) -->")
    A("- [ ] 인터페이스 명세가 최신화되었는가? <!-- SRS §6.1 서버 진입점 · §6.2 Prisma 스키마 -->")
    A("- [ ] Vercel 프리뷰 배포가 성공했는가? <!-- 빌드 실패 = 배포 차단 (C-TEC-007 · ADR-T08) -->")
    A("- [ ] 관련 계측 이벤트가 적재되는가? <!-- 해당 시 · SRS §10.2 -->")
    for d in spec.get("dod_extra", []):
        A(f"- [ ] {d}")
    A("")

    # 🚧 Dependencies
    A("## 🚧 Dependencies & Blockers")
    dep = " · ".join(f"#<이슈번호> ({x})" for x in deps) or "없음"
    blk = " · ".join(f"#<이슈번호> ({x})" for x in sorted(BLOCKS.get(tid, []))) or "없음"
    A(f"- Depends on: {dep}")
    A(f"- Blocks: {blk}")
    A(f"- External Blocker: {spec.get('external', '없음')}")
    nb = len(BLOCKS.get(tid, []))
    if nb >= 6:
        A(f"- ⚠️ **후행 {nb}건** — 이 태스크가 밀리면 {nb}개가 함께 밀린다.")
    if spec.get("note"):
        A(f"- {spec['note']}")
    return "\n".join(L) + "\n"


def main():
    targets = [a for a in sys.argv[1:] if not a.startswith("-")] or list(BY)
    missing = [t for t in targets if t not in S.SPECS]
    if missing:
        print("명세 미작성:", " ".join(missing))
        return 1
    os.makedirs(OUT, exist_ok=True)
    for tid in targets:
        with open(os.path.join(OUT, f"{tid}.md"), "w", encoding="utf-8") as f:
            f.write(render(tid))
    print(f"생성 {len(targets)}건 → {OUT}/")
    total = len(BY)
    done = len([t for t in BY if t in S.SPECS])
    print(f"명세 진척: {done}/{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
