#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""마크다운 링크와 앵커의 무결성을 검사한다.

문서를 옮기거나 이름을 바꾸면 링크가 조용히 깨진다. 렌더링은 멀쩡해
보이므로 눈으로는 못 잡는다. 이 스크립트를 이동 작업 뒤에 반드시 돌린다.

    python3 tools/verify_links.py

리포 밖(../VPS 등)을 가리키는 링크는 EXTERNAL 로 분류해 실패로 세지
않는다. 원본 PRD 가 다른 작업공간에서 작성될 때 걸린 링크로, 이 저장소가
해결할 수 있는 대상이 아니다.
"""
import os, re, sys, json, collections, urllib.parse

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".next"}


def vendored_skills():
    """마켓플레이스에서 설치한 스킬 디렉터리.

    `npx skills add` 가 받아온 서드파티 문서라 내부 링크는 우리가 고칠 대상이
    아니다. skills-lock.json 이 설치 목록의 원천이므로 이름을 거기서 읽는다."""
    try:
        with open("skills-lock.json", encoding="utf-8") as f:
            names = json.load(f).get("skills", {}).keys()
    except (OSError, ValueError):
        return set()
    return {os.path.normpath(f".agents/skills/{n}") for n in names}
EXTERNAL_PREFIX = ("../VPS/", "../JTBD/", "../OS/", "../CJM/", "../Persona/")


def slug(h):
    s = re.sub(r'[`*_~]', '', h.strip().lower())
    s = re.sub(r'[^\w\s\-가-힣ㄱ-ㅎㅏ-ㅣ]', '', s, flags=re.U)
    return s.replace(' ', '-')


def strip_code(t):
    """코드 펜스와 인라인 코드를 지운다.

    README 의 `[텍스트](URL)` 처럼 링크 문법을 설명하는 예시가 백틱 안에
    들어 있으면 실제 링크로 오인된다. 줄 수는 유지해야 L 번호가 맞으므로
    개행은 남긴다."""
    t = re.sub(r'```.*?```', lambda m: "\n" * m.group(0).count("\n"), t, flags=re.S)
    return re.sub(r'`[^`\n]*`', '', t)


def md_files():
    skip = vendored_skills()
    out = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS
                   and os.path.normpath(os.path.join(root, d)[2:]) not in skip]
        out += [os.path.join(root, f)[2:] for f in files if f.endswith(".md")]
    return sorted(out)


def main():
    files = md_files()
    anchors = {}
    for p in files:
        t = open(p, encoding="utf-8").read()
        a = {slug(m.group(2)) for m in re.finditer(r'^(#{1,6})\s+(.+?)\s*$', t, re.M)}
        a |= {m.group(1).lower()
              for m in re.finditer(r'<a\s+(?:id|name)=["\']([^"\']+)["\']', t)}
        anchors[p] = a

    broken, external, total = collections.defaultdict(list), 0, 0
    for p in files:
        t = strip_code(open(p, encoding="utf-8").read())
        for m in re.finditer(r'\]\(\s*(?!https?:|mailto:)([^)\s#]*)(#[^)\s]*)?\s*\)', t):
            path, anc = m.group(1) or "", m.group(2) or ""
            if not path and not anc:
                continue
            total += 1
            ln = t[:m.start()].count("\n") + 1
            fp = p
            if path:
                if path.startswith(EXTERNAL_PREFIX):
                    external += 1
                    continue
                tgt = urllib.parse.unquote(path)
                base = "." if tgt.startswith("/") else os.path.dirname(p)
                fp = os.path.normpath(os.path.join(base, tgt.lstrip("/")))
                if not os.path.exists(fp):
                    broken[p].append((ln, path + anc, "파일 없음"))
                    continue
            if anc and fp.endswith(".md") and fp in anchors:
                if urllib.parse.unquote(anc[1:]).lower() not in anchors[fp]:
                    broken[p].append((ln, path + anc, "앵커 없음"))

    n = sum(len(v) for v in broken.values())
    print(f"문서 {len(files)}개 · 내부 링크 {total}건 · 리포 밖 참조 {external}건 제외"
          f" · 설치 스킬 {len(vendored_skills())}종 제외")
    for p in sorted(broken):
        print(f"■ {p}")
        for ln, tgt, why in broken[p]:
            print(f"    L{ln:<5} {why}  →  {tgt}")
    print("\n" + (f"❌ 깨진 링크 {n}건" if n else "통과 — 깨진 링크 없음"))
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
