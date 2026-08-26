#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub Project(v2)에 태스크 59건을 등록하고 일정 필드를 채운다.

`project` 스코프가 필요하다:  gh auth refresh -s project

사용법:
    python3 tools/gh_sync_project.py --fields   # 필드 생성
    python3 tools/gh_sync_project.py --add      # 이슈를 프로젝트에 추가
    python3 tools/gh_sync_project.py --values   # 필드 값 주입
    python3 tools/gh_sync_project.py --all      # 위 세 단계 순차 실행
"""
import sys, os, json, subprocess, time

OWNER, NUMBER = "wild-mental", "25"
REPO = "wild-mental/ai-place-mate-prd-to-srs"
S = json.load(open("/tmp/schedule.json"))
T = S["tasks"]
M = json.load(open("/tmp/issue_map.json"))

TRACK = {"platform": "플랫폼", "backend": "백엔드", "frontend": "프론트엔드",
         "design": "디자인", "qa": "QA"}
PHASE = {"P0": "P0 기반·계약", "P1": "P1 클로즈드 베타",
         "P1-late": "P1 말 · 예약·결제", "P2": "P2 오픈 베타"}

# (이름, 타입, 옵션)
# 내장 필드는 재사용한다 — Start date / Target date(DATE) · Estimate(NUMBER, 일수)
# · Size(SINGLE_SELECT, 복잡도) · Status. 아래는 신설 대상만.
FIELDS = [
    ("Week", "NUMBER", None),
    ("Track", "SINGLE_SELECT", list(TRACK.values())),
    ("Lane", "TEXT", None),
    ("Epic", "SINGLE_SELECT", ["INF", "TEC", "CTR", "DAT", "MCK", "QRY", "EVD", "RNK",
                               "RSV", "MCH", "AGR", "ANA", "SEC", "REL", "TST", "UX"]),
    ("Task type", "SINGLE_SELECT", ["Contract", "Data", "Read", "Write", "UI",
                                    "Test", "Infra", "NFR", "Design"]),
    ("Phase", "SINGLE_SELECT", list(PHASE.values())),
    ("Sprint", "SINGLE_SELECT", ["S-1", "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]),
    ("Critical path", "SINGLE_SELECT", ["Yes", "No"]),
    ("Complexity note", "TEXT", None),
    ("Depends on", "TEXT", None),
    ("Blocks", "TEXT", None),
    ("Task ID", "TEXT", None),
]


def gql(q, **kw):
    cmd = ["gh", "api", "graphql", "-f", f"query={q}"]
    for k, v in kw.items():
        cmd += ["-f", f"{k}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"GraphQL 실패: {r.stderr[:300]}")
    return json.loads(r.stdout)


def project_id():
    q = ('query($o:String!,$n:Int!){user(login:$o){projectV2(number:$n){id title}}}')
    r = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}",
                        "-F", f"o={OWNER}", "-F", f"n={NUMBER}"], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"프로젝트 조회 실패: {r.stderr[:300]}")
    d = json.loads(r.stdout)["data"]["user"]["projectV2"]
    return d["id"], d["title"]


def mk_fields():
    pid, title = project_id()
    print(f"프로젝트: {title} ({pid})")
    exist = json.loads(subprocess.run(
        ["gh", "project", "field-list", NUMBER, "--owner", OWNER, "--format", "json", "-L", "100"],
        capture_output=True, text=True).stdout)["fields"]
    have = {f["name"] for f in exist}
    for name, typ, opts in FIELDS:
        if name in have:
            print(f"  = {name} (이미 있음)")
            continue
        cmd = ["gh", "project", "field-create", NUMBER, "--owner", OWNER,
               "--name", name, "--data-type", typ]
        if opts:
            cmd += ["--single-select-options", ",".join(opts)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(f"  {'✅' if r.returncode == 0 else '❌'} {name} ({typ})"
              + ("" if r.returncode == 0 else f" {r.stderr.strip()[:100]}"))
        time.sleep(0.3)


def add_items():
    done = json.load(open("/tmp/item_map.json")) if os.path.exists("/tmp/item_map.json") else {}
    for tid, num in sorted(M.items(), key=lambda kv: kv[1]):
        if tid in done:
            continue
        url = f"https://github.com/{REPO}/issues/{num}"
        r = subprocess.run(["gh", "project", "item-add", NUMBER, "--owner", OWNER,
                            "--url", url, "--format", "json"], capture_output=True, text=True)
        if r.returncode:
            print(f"  ❌ {tid}: {r.stderr.strip()[:120]}")
            continue
        done[tid] = json.loads(r.stdout)["id"]
        json.dump(done, open("/tmp/item_map.json", "w"))
        print(f"  ✅ {tid} → item")
        time.sleep(0.35)
    print(f"추가 완료 {len(done)}/{len(M)}")


def set_values():
    pid, _ = project_id()
    items = json.load(open("/tmp/item_map.json"))
    fl = json.loads(subprocess.run(
        ["gh", "project", "field-list", NUMBER, "--owner", OWNER, "--format", "json", "-L", "100"],
        capture_output=True, text=True).stdout)["fields"]
    F = {f["name"]: f for f in fl}

    def val(tid):
        v = T[tid]
        return {
            "Task ID": ("text", tid),
            "Start date": ("date", v["start"]),
            "Target date": ("date", v["end"]),
            "Estimate": ("number", v["duration"]),
            "Size": ("opt", {"H": "L", "M": "M", "L": "XS"}[v["complexity"]]),
            "Status": ("opt", "Backlog"),
            "Priority": ("opt", "P0" if v["critical"] else
                         ("P1" if len(v["blocks"]) >= 3 else "P2")),
            "Week": ("number", v["week"]),
            "Track": ("opt", TRACK[v["track"]]),
            "Lane": ("text", v["lane"]),
            "Epic": ("opt", tid.split("-")[0]),
            "Task type": ("opt", v["type"]),
            "Complexity note": ("text", f"{v['complexity']} · {v['duration']}d"),
            "Phase": ("opt", PHASE[v["phase"]]),
            "Sprint": ("opt", v["sprint"]),
            "Critical path": ("opt", "Yes" if v["critical"] else "No"),
            "Depends on": ("text", " ".join(v["deps"]) or "—"),
            "Blocks": ("text", " ".join(v["blocks"]) or "—"),
        }

    # 항목 하나의 필드 18개를 alias로 묶어 단일 뮤테이션으로 보낸다.
    # 필드마다 따로 호출하면 59×18 = 약 940회가 되어 GraphQL 한도(5000점)를
    # 태운다. 묶으면 59회로 떨어진다.
    def mutation(iid, fields):
        parts = []
        for n, (fid, lit) in enumerate(fields):
            parts.append(f'a{n}:updateProjectV2ItemFieldValue(input:{{'
                         f'projectId:$p,itemId:$i,fieldId:{json.dumps(fid)},'
                         f'value:{{{lit}}}}}){{clientMutationId}}')
        return "mutation($p:ID!,$i:ID!){" + " ".join(parts) + "}"

    ok = err = 0
    failed = []
    for tid, iid in sorted(items.items()):
        fields = []
        for fname, (kind, value) in val(tid).items():
            f = F.get(fname)
            if not f:
                continue
            if kind == "opt":
                o = next((x for x in f.get("options", []) if x["name"] == str(value)), None)
                if not o:
                    continue
                lit = f'singleSelectOptionId:{json.dumps(o["id"])}'
            elif kind == "date":
                lit = f'date:{json.dumps(str(value))}'
            elif kind == "number":
                lit = f'number:{float(value)}'
            else:
                lit = f'text:{json.dumps(str(value))}'
            fields.append((f["id"], lit))

        q = mutation(iid, fields)
        for attempt in range(4):
            r = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}",
                                "-F", f"p={pid}", "-F", f"i={iid}"],
                               capture_output=True, text=True)
            if r.returncode == 0:
                break
            # 2차 한도(secondary rate limit)는 잠깐 쉬면 풀린다.
            if "rate limit" in r.stderr.lower() and attempt < 3:
                wait = 60 * (attempt + 1)
                print(f"  … 한도 대기 {wait}s ({tid})", flush=True)
                time.sleep(wait)
                continue
            break
        if r.returncode == 0:
            ok += 1
            print(f"  ✅ {tid} ({len(fields)}개 필드)", flush=True)
        else:
            err += 1
            failed.append(tid)
            print(f"  ❌ {tid} :: {r.stderr.strip()[:160]}", flush=True)
        time.sleep(0.5)

    print(f"필드 값 주입: 성공 {ok} · 실패 {err}")
    if failed:
        print("실패 태스크: " + " ".join(failed))


if __name__ == "__main__":
    a = sys.argv
    if "--fields" in a or "--all" in a:
        mk_fields()
    if "--add" in a or "--all" in a:
        add_items()
    if "--values" in a or "--all" in a:
        set_values()
