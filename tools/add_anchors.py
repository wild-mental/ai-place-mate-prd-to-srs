#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SRS 문서의 요구사항 ID에 HTML 앵커를 삽입한다.

태스크 문서의 References가 `...md#REQ-FUNC-001` 로 특정 요구사항을 가리킬 수 있게 한다.
요구사항이 표 행에 있어 마크다운 제목 앵커가 생기지 않으므로 인라인 앵커를 쓴다.
멱등 — 이미 앵커가 있으면 건너뛴다.

사용법:
    python3 tools/add_anchors.py           # 삽입
    python3 tools/add_anchors.py --check   # 누락만 보고 (변경 없음)
"""
import sys, re

TARGETS = [
    "docs/tech-design-docs/[SRS]AI-Place-Mate-SRS-v1_0.md",
    "docs/tech-design-docs/[SRS]AI-Place-Mate-SRS-v0_1.md",
]
# 요구사항 표의 첫 열: | **REQ-FUNC-001** |  또는  | **REQ-NF-001a** |
ROW = re.compile(r'^\|\s*(?!<a )\*\*(REQ-(?:FUNC|NF|TEC)-\d+[ab]?)\*\*\s*\|')


def process(path, check):
    lines = open(path, encoding="utf-8").read().split("\n")
    added, existing = [], []
    for i, l in enumerate(lines):
        if "<a id=\"REQ-" in l:
            existing.append(re.search(r'<a id="(REQ-[^"]+)"', l).group(1))
            continue
        m = ROW.match(l)
        if m:
            rid = m.group(1)
            if not check:
                lines[i] = l.replace(f"**{rid}**", f'<a id="{rid}"></a>**{rid}**', 1)
            added.append(rid)
    if not check and added:
        open(path, "w", encoding="utf-8").write("\n".join(lines))
    return added, existing


def main():
    check = "--check" in sys.argv
    total = 0
    for p in TARGETS:
        added, existing = process(p, check)
        total += len(added)
        name = p.split("/")[-1]
        if check:
            print(f"{name}: 앵커 있음 {len(existing)} · 없음 {len(added)}")
            if added:
                print("   누락:", ", ".join(added))
        else:
            print(f"{name}: 앵커 {len(added)}개 삽입 (기존 {len(existing)}개 유지)")
            if added:
                print("   " + ", ".join(added))
    if check and total:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
