#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""태스크 문서 59건을 GitHub Issue 로 등록하고 의존성을 실제 이슈 번호로 연결한다.

사용법:
    python3 tools/gh_sync_issues.py --dry TASK-ID   # 본문 미리보기
    python3 tools/gh_sync_issues.py --create        # 전량 생성
    python3 tools/gh_sync_issues.py --link          # Depends/Blocks 를 실제 #번호로 치환
"""
import sys, os, re, json, subprocess, time

REPO = "wild-mental/ai-place-mate-prd-to-srs"
DOCS = "docs/tasks"
S = json.load(open("/tmp/schedule.json"))
T = S["tasks"]
MAP_FILE = "/tmp/issue_map.json"
MS_TITLE = {"S-1": "S-1 기반 · 게이트 구축", "S0": "S0 계약 · 스키마", "S1": "S1 색인 · 계측",
            "S2": "S2 필터 · 메뉴", "S3": "S3 파싱 · 근거", "S4": "S4 Top-3 · 관측",
            "S5": "S5 예약 승계", "S6": "S6 결제", "S7": "S7 가맹 콘솔", "S8": "S8 대화방"}
BASE = "https://github.com/wild-mental/ai-place-mate-prd-to-srs/blob/main"


def body(tid):
    raw = open(f"{DOCS}/{tid}.md", encoding="utf-8").read()
    # YAML 프론트매터 제거 (이슈 본문에는 불필요)
    raw = re.sub(r"^---\n.*?\n---\n\n?", "", raw, count=1, flags=re.S)
    v = T[tid]
    cp = " · ⚠️ **임계 경로**" if v["critical"] else ""
    hdr = [
        f"> **{tid}** · `{v['type']}` · 복잡도 `{v['complexity']}` · {v['duration']}일{cp}",
        "",
        "| 항목 | 값 |",
        "| --- | --- |",
        f"| 트랙 | {v['track']} (`{v['lane']}`) |",
        f"| 스프린트 · Phase | `{v['sprint']}` · `{v['phase']}` |",
        f"| 일정 (압축안) | **{v['start']} ~ {v['end']}** (W{v['week']} 착수) |",
        f"| 선행 | {' · '.join(f'`{x}`' for x in v['deps']) or '없음'} |",
        f"| 후행 | {' · '.join(f'`{x}`' for x in v['blocks']) or '없음'} |",
        "",
        f"📄 원본 명세: [`docs/tasks/{tid}.md`]({BASE}/docs/tasks/{tid}.md) · "
        f"📋 [태스크 리스트]({BASE}/docs/%5B%ED%83%9C%EC%8A%A4%ED%81%AC%20%EB%A6%AC%EC%8A%A4%ED%8A%B8%5D%20AI-Place-Mate.md#{tid}) · "
        f"🗓️ [압축 수행 일정]({BASE}/docs/%5B%EC%B4%9D%EA%B4%84%5D%20%EC%95%95%EC%B6%95%20%EC%88%98%ED%96%89%20%EC%9D%BC%EC%A0%95.md)",
        "",
        "---",
        "",
    ]
    return "\n".join(hdr) + raw


def labels(tid):
    v = T[tid]
    ls = [f"epic:{tid.split('-')[0]}", f"part:{v['part']}", f"complexity:{v['complexity']}",
          f"phase:{v['phase']}", f"type:{v['type']}"]
    if v["critical"]:
        ls.append("critical-path")
    return ls


def create():
    done = json.load(open(MAP_FILE)) if os.path.exists(MAP_FILE) else {}
    order = sorted(T, key=lambda t: (T[t]["start"], t))
    for i, tid in enumerate(order, 1):
        if tid in done:
            continue
        v = T[tid]
        f = f"/tmp/body_{tid}.md"
        open(f, "w", encoding="utf-8").write(body(tid))
        cmd = ["gh", "issue", "create", "-R", REPO,
               "-t", f"[{tid}] {v['feature']}", "-F", f,
               "-m", MS_TITLE[v["sprint"]]]
        for l in labels(tid):
            cmd += ["-l", l]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ❌ {tid}: {r.stderr.strip()[:140]}")
            continue
        num = int(r.stdout.strip().rsplit("/", 1)[-1])
        done[tid] = num
        json.dump(done, open(MAP_FILE, "w"))
        print(f"  ✅ #{num:<3} {tid}  {v['feature'][:44]}")
        time.sleep(0.6)
    print(f"생성 완료 {len(done)}/{len(T)}")


def link():
    m = json.load(open(MAP_FILE))
    for tid, num in sorted(m.items(), key=lambda kv: kv[1]):
        b = subprocess.run(["gh", "issue", "view", str(num), "-R", REPO, "--json", "body",
                            "--jq", ".body"], capture_output=True, text=True).stdout
        def sub(mt):
            ref = mt.group(1)
            return f"#{m[ref]} (`{ref}`)" if ref in m else mt.group(0)
        nb = re.sub(r"#<이슈번호> \(([A-Z]{2,3}-\d{3})\)", sub, b)
        nb = re.sub(r"#<이슈번호> \(([A-Z]{2,3}-\d{3}) —", lambda x: f"#{m[x.group(1)]} (`{x.group(1)}` —"
                    if x.group(1) in m else x.group(0), nb)
        if nb == b:
            continue
        open("/tmp/nb.md", "w", encoding="utf-8").write(nb)
        r = subprocess.run(["gh", "issue", "edit", str(num), "-R", REPO, "-F", "/tmp/nb.md"],
                           capture_output=True, text=True)
        print(f"  {'✅' if r.returncode == 0 else '❌'} #{num} {tid}")
        time.sleep(0.4)


if __name__ == "__main__":
    if "--dry" in sys.argv:
        tid = sys.argv[sys.argv.index("--dry") + 1]
        print(body(tid)[:1400])
        print("\n[LABELS]", labels(tid))
    elif "--create" in sys.argv:
        create()
    elif "--link" in sys.argv:
        link()
