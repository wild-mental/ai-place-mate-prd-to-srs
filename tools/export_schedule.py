#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""압축 수행 일정(PLAN-AIPLACE-FAST-001)을 GitHub 연동용 JSON으로 내보낸다."""
import sys, os, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util as iu
spec = iu.spec_from_file_location("ft", os.path.join(os.path.dirname(__file__), "gen_fasttrack_plan.py"))
G = iu.module_from_spec(spec); spec.loader.exec_module(G)

PHASE = {"S-1": "P0", "S0": "P0", "S1": "P1", "S2": "P1", "S3": "P1", "S4": "P1",
         "S5": "P1-late", "S6": "P1-late", "S7": "P2", "S8": "P2"}
RN = {"PLT": "platform", "BE": "backend", "FE": "frontend", "DSG": "design", "QA": "qa"}
PART = {"PLT": "infra", "BE": "backend", "FE": "frontend", "DSG": "design", "QA": "backend"}

out = {"tasks": {}, "meta": {}}
for t in G.IDS:
    _, feature, refs, deps, cx, ty, sp = G.BY[t]
    r = G.role[t]
    out["tasks"][t] = {
        "feature": feature, "refs": refs, "deps": deps, "blocks": sorted(G.BLOCKS.get(t, [])),
        "complexity": cx, "type": ty, "sprint": sp, "phase": PHASE[sp],
        "role": r, "track": RN[r], "part": PART[r], "lane": f"{RN[r]}{G.LANE[t][1]+1}",
        "duration": G.dur[t],
        "start": str(G.workday(G.S[t])), "end": str(G.workday(G.F[t] - 1)),
        "week": G.S[t] // 5 + 1, "critical": t in G.CP,
    }
# 스프린트 마일스톤 마감일 = 해당 스프린트 태스크의 최종 종료일
ms = {}
for t in G.IDS:
    sp = G.BY[t][6]
    d = out["tasks"][t]["end"]
    if sp not in ms or d > ms[sp]:
        ms[sp] = d
out["milestones"] = ms
out["meta"] = {"span": G.SPAN, "headcount": sum(G.FAST.values()), "cp": G.CP,
               "start": str(G.workday(0)), "end": str(G.workday(G.SPAN - 1))}
json.dump(out, open("/tmp/schedule.json", "w"), ensure_ascii=False, indent=1)
print(f"태스크 {len(out['tasks'])}건 · 마일스톤 {len(ms)}개 · {out['meta']['start']} ~ {out['meta']['end']}")
print("스프린트 마감일:", {k: ms[k] for k in G.D.SPRINT_ORDER if k in ms})
