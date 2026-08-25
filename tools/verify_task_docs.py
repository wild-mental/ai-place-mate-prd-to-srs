#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""태스크 이슈 문서(docs/tasks/*.md) 검증.

  1) 템플릿 7개 섹션의 존재와 순서
  2) 프론트매터 title/labels 실제 값 치환
  3) 미치환 플레이스홀더 (백틱 코드 구간은 제외)
  4) References 앵커가 대상 문서에 실재하는지
  5) Depends on / Blocks 가 tasks_data.py 단일 원천과 일치하는지
  6) AC 정상·실패 시나리오 각 1건 이상
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tasks_data as D  # noqa: E402

TPL = ".github/ISSUE_TEMPLATE/feature-task.md"
DIR = "docs/tasks"
BY = {t[0]: t for t in D.TASKS}
BLOCKS = {}
for tid, _, _, deps, _, _, _ in D.TASKS:
    for d in deps:
        BLOCKS.setdefault(d, []).append(tid)

ANCHOR_DOCS = {
    "[태스크 리스트] AI-Place-Mate.md": "docs/[태스크 리스트] AI-Place-Mate.md",
    "[SRS 문서] AI-Place-Mate (기술제약 반영판).md": "docs/[SRS 문서] AI-Place-Mate (기술제약 반영판).md",
    "[SRS 문서] AI-Place-Mate (한글).md": "docs/[SRS 문서] AI-Place-Mate (한글).md",
    "[설계 문서] AI-Place-Mate (한글).md": "docs/[설계 문서] AI-Place-Mate (한글).md",
}


def slug(h):
    """GitHub 마크다운 앵커 규칙 — 구두점 제거 후 공백을 '개별' 치환한다.
    공백을 collapse 하면 이중 하이픈(예: `31-erd--개체와-관계`)을 놓친다."""
    s = h.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return s.replace(" ", "-")


def doc_anchors(path):
    txt = open(path, encoding="utf-8").read()
    a = set(re.findall(r'<a id="([^"]+)"', txt))
    for h in re.findall(r"^#{1,6}\s+(.*)$", txt, re.M):
        a.add(slug(h))
    return a


def strip_code(s):
    return re.sub(r"`[^`]*`", "``", s)


def main():
    tpl_secs = [l for l in open(TPL, encoding="utf-8").read().split("\n") if l.startswith("## ")]
    anchors = {k: doc_anchors(v) for k, v in ANCHOR_DOCS.items() if os.path.exists(v)}
    errs, n = [], 0
    for f in sorted(os.listdir(DIR)):
        if not f.endswith(".md"):
            continue
        n += 1
        tid = f[:-3]
        p = os.path.join(DIR, f)
        s = open(p, encoding="utf-8").read()
        secs = [l for l in s.split("\n") if l.startswith("## ")]
        if secs != tpl_secs:
            errs.append(f"{tid}: 섹션 구성/순서 불일치")
        if f'title: "[Feature] {tid}:' not in s:
            errs.append(f"{tid}: 프론트매터 title 미치환")
        body = strip_code(s.split("## 🎯")[-1])
        body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
        ph = [x for x in re.findall(r"<[^>\n]{1,60}>", body)
              if "이슈번호" not in x and not x.startswith("<a ") and not x.startswith("</")]
        if ph:
            errs.append(f"{tid}: 미치환 플레이스홀더 {ph[:3]}")
        # References 앵커
        for docname, anc in anchors.items():
            for m in re.findall(re.escape(docname) + r"#([A-Za-z0-9가-힣_-]+)", s):
                if m not in anc:
                    errs.append(f"{tid}: 앵커 미해결 {docname}#{m}")
        # 의존성 정합
        rec = BY.get(tid)
        if not rec:
            errs.append(f"{tid}: tasks_data 에 없는 태스크")
            continue
        dep_sec = s.split("## 🚧")[-1]
        P = r"(?:INF|TEC|CTR|DAT|MCK|QRY|EVD|RNK|RSV|MCH|AGR|ANA|SEC|REL|TST|UX)-\d{3}"
        dline = [l for l in dep_sec.split("\n") if l.startswith("- Depends on:")]
        bline = [l for l in dep_sec.split("\n") if l.startswith("- Blocks:")]
        got_d = set(re.findall(P, dline[0])) if dline else set()
        got_b = set(re.findall(P, bline[0])) if bline else set()
        if got_d != set(rec[3]):
            errs.append(f"{tid}: Depends 불일치 문서{sorted(got_d)} ≠ 원천{sorted(rec[3])}")
        if got_b != set(BLOCKS.get(tid, [])):
            errs.append(f"{tid}: Blocks 불일치 문서{sorted(got_b)} ≠ 원천{sorted(BLOCKS.get(tid, []))}")
        # AC 시나리오
        sc = re.findall(r"^Scenario \d+.*$", s, re.M)
        fail = [x for x in sc if "실패" in x]
        if len(sc) < 2:
            errs.append(f"{tid}: Scenario {len(sc)}건 (2건 이상 필요)")
        if not fail:
            errs.append(f"{tid}: 실패 흐름 Scenario 없음")
        print(f"  {tid}: 섹션 {len(secs)}/{len(tpl_secs)} · Scenario {len(sc)}(실패 {len(fail)}) "
              f"· Depends {len(got_d)} · Blocks {len(got_b)}")
    print(f"\n태스크 문서 {n}건")
    if errs:
        print("검증 실패:")
        for e in errs:
            print("  ✗", e)
        return 1
    print("검증 통과: 템플릿 준수 · 앵커 해결 · 의존성 원천 일치 · 실패 시나리오 보유")
    return 0


if __name__ == "__main__":
    sys.exit(main())
