#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""문서 정합성 검증 — GFM 표 열 수, mermaid 블록 추출, 요구사항 ID 교차 참조.

사용법:
    python3 tools/verify_docs.py                 # 표·펜스·교차 참조 검증
    python3 tools/verify_docs.py --dump-mermaid DIR   # mermaid 블록을 파일로 추출
                                                     # (mmdc 로 렌더 검증용)
"""
import re, sys, os, glob

DOCS = [
    "ai-place-prd-v1_0.md",
    "docs/[SRS 문서] AI-Place-Mate (한글).md",
    "docs/[SRS 문서] AI-Place-Mate (기술제약 반영판).md",
    "docs/[설계 문서] AI-Place-Mate (한글).md",
    "docs/[태스크 리스트] AI-Place-Mate.md",
    "docs/[분석] 태스크 추출 방법론 적합성 평가.md",
    "docs/[분석] 태스크 축약 가능성 검토.md",
    "docs/[총괄] 개발 실행 계획.md",
    "docs/[총괄] 압축 수행 일정.md",
    "README.md",
]

def cell_count(line):
    """GFM 표의 열 구분자 수. `\\|` 이스케이프는 세지 않는다."""
    return line.replace('\\|', '\x00').count('|')

def check_tables(path, lines):
    bad = tables = 0
    i = 0
    while i < len(lines):
        if lines[i].startswith('|') and i + 1 < len(lines) \
           and re.match(r'^\|( --- \|)+$', lines[i + 1]):
            tables += 1
            n = cell_count(lines[i])
            j = i
            while j < len(lines) and lines[j].startswith('|'):
                if cell_count(lines[j]) != n:
                    print(f'  [표 열 불일치] {path}:{j+1}  {lines[j][:70]}')
                    bad += 1
                j += 1
            i = j
        else:
            i += 1
    return tables, bad

def mermaid_blocks(lines):
    blocks = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == '```mermaid':
            j = i + 1
            while j < len(lines) and lines[j].strip() != '```':
                j += 1
            blocks.append((i + 1, '\n'.join(lines[i + 1:j])))
            i = j
        i += 1
    return blocks

def main():
    dump = None
    if '--dump-mermaid' in sys.argv:
        dump = sys.argv[sys.argv.index('--dump-mermaid') + 1]
        os.makedirs(dump, exist_ok=True)
        for f in glob.glob(os.path.join(dump, '*.mmd')):
            os.remove(f)

    total_bad = 0
    req_ids = {}
    for path in DOCS:
        if not os.path.exists(path):
            print(f'  [없음] {path}')
            continue
        text = open(path, encoding='utf-8').read()
        lines = text.split('\n')
        tables, bad = check_tables(path, lines)
        total_bad += bad
        blocks = mermaid_blocks(lines)
        # 줄 시작의 펜스만 센다 — 표 셀 안의 인라인 코드는 펜스가 아니다
        fences = sum(1 for l in lines if l.lstrip().startswith('```'))
        if fences % 2:
            print(f'  [코드 펜스 홀수] {path}')
            total_bad += 1
        req_ids[path] = set(re.findall(r'REQ-(?:FUNC|NF)-\d+', text))
        print(f'{os.path.basename(path)}: {len(lines)}줄 · 표 {tables}개 '
              f'· 열 불일치 {bad}건 · mermaid {len(blocks)}개')
        if dump:
            tag = ('TEC' if '기술제약' in path else 'SRS') if 'SRS' in path \
                else 'SDD' if '설계' in path else 'PLAN' if '총괄' in path else 'ANL' if '분석' in path else 'TASK' if '태스크' in path else 'PRD'
            for k, (ln, body) in enumerate(blocks, 1):
                out = os.path.join(dump, f'{tag}_{k:02d}_L{ln}.mmd')
                open(out, 'w', encoding='utf-8').write(body + '\n')

    # 앵커 무결성 — 태스크 리스트가 참조하는 앵커가 SRS에 실재하는가
    import re as _re
    anchors = set()
    for _p in ["docs/[SRS 문서] AI-Place-Mate (기술제약 반영판).md",
               "docs/[SRS 문서] AI-Place-Mate (한글).md",
               "docs/[태스크 리스트] AI-Place-Mate.md"]:
        if os.path.exists(_p):
            anchors |= set(_re.findall(r'<a id="([^"]+)"', open(_p, encoding="utf-8").read()))
    print(f'\n인라인 앵커 {len(anchors)}개 (요구사항 + 태스크)')

    srs = req_ids.get("docs/[SRS 문서] AI-Place-Mate (한글).md", set())
    sdd = req_ids.get("docs/[설계 문서] AI-Place-Mate (한글).md", set())
    orphan = sorted(sdd - srs)
    print(f'\nSRS 요구사항 ID {len(srs)}건 · SDD 참조 {len(sdd)}건')
    if orphan:
        print(f'  [SDD가 SRS에 없는 ID 참조] {orphan}')
        total_bad += len(orphan)
    else:
        print('  SDD의 모든 요구사항 참조가 SRS에 존재')

    if dump:
        print(f'\nmermaid 블록을 {dump}/ 에 추출했습니다. 렌더 검증:')
        print('  npm install @mermaid-js/mermaid-cli')
        print('  npx puppeteer browsers install chrome-headless-shell')
        print(f'  for f in {dump}/*.mmd; do npx mmdc -i "$f" -o /tmp/x.svg || echo "FAIL $f"; done')

    print(f'\n{"통과" if total_bad == 0 else f"실패 {total_bad}건"}')
    return 1 if total_bad else 0

if __name__ == '__main__':
    sys.exit(main())
