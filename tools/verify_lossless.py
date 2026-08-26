# -*- coding: utf-8 -*-
"""HTML 슬라이드 본문 vs 생성된 MD 의 토큰 시퀀스 비교"""
import re, html, difflib
from html.parser import HTMLParser

raw=open('docs/source-docs/[PRD]AI-Place-Mate-PRD-v0_1.html',encoding='utf-8').read()
raw=re.sub(r'<!--.*?-->','',raw,flags=re.S)
# 슬라이드 섹션만 추출
sections=re.findall(r'<section class="slide">(.*?)</section>', raw, flags=re.S)
h=''.join(sections)
h=re.sub(r'<(script|style)[^>]*>.*?</\1>','',h,flags=re.S)
h=html.unescape(re.sub(r'<[^>]+>',' ',h))

m=open('docs/source-docs/[PRD]AI-Place-Mate-PRD-v0_1.md',encoding='utf-8').read()
# 변환기가 덧붙인 머리말·슬라이드 주석만 제거
m=re.sub(r'^# .*?\n(> .*\n)+','',m,count=1)
m=re.sub(r'<!-- 슬라이드 \d+ / \d+ -->','',m)
# 마크다운 문법 문자 제거
m=re.sub(r'```mermaid|```','',m)
m=re.sub(r'^[>\-#|]+',' ',m,flags=re.M)
m=m.replace('\\|',' ')

TOK=re.compile(r'[0-9A-Za-z가-힣]+')
def toks(s): return TOK.findall(s)

a,b=toks(h),toks(m)
print(f'HTML 토큰 {len(a)} / MD 토큰 {len(b)}')
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
missing=[];added=[]
for op,i1,i2,j1,j2 in sm.get_opcodes():
    if op in ('delete','replace'): missing += a[i1:i2]
    if op in ('insert','replace'): added   += b[j1:j2]
print(f'HTML에만 있는 토큰(손실) {len(missing)}개')
if missing: print('  ->', missing[:80])
print(f'MD에만 있는 토큰(추가)   {len(added)}개')
if added: print('  ->', added[:80])
print('ratio', round(sm.ratio(),6))
