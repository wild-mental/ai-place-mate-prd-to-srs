# -*- coding: utf-8 -*-
"""docs/source-docs/[PRD]AI-Place-Mate-PRD-v0_1.html -> Markdown (구조 보존 변환기)"""
import re, sys, html
from html.parser import HTMLParser

SRC = 'docs/source-docs/[PRD]AI-Place-Mate-PRD-v0_1.html'
OUT = 'docs/source-docs/[PRD]AI-Place-Mate-PRD-v0_1.md'

VOID = {'br','hr','img','meta','link','input','i'}

class Node:
    __slots__=('tag','cls','style','attrs','children','parent','text')
    def __init__(self, tag, attrs=None, parent=None):
        self.tag=tag; self.attrs=dict(attrs or {})
        self.cls=set((self.attrs.get('class') or '').split())
        self.style=self.attrs.get('style','')
        self.children=[]; self.parent=parent; self.text=None
    def __repr__(self): return f'<{self.tag} {sorted(self.cls)}>'

class Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root=Node('#root'); self.cur=self.root
    def handle_starttag(self, tag, attrs):
        n=Node(tag, attrs, self.cur); self.cur.children.append(n)
        if tag not in VOID: self.cur=n
    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))
    def handle_endtag(self, tag):
        if tag in VOID: return
        n=self.cur
        while n is not self.root and n.tag!=tag: n=n.parent
        if n is not self.root: self.cur=n.parent
    def handle_data(self, data):
        t=Node('#text', None, self.cur); t.text=data
        self.cur.children.append(t)

def ws(s):
    return re.sub(r'[ \t\r\f\v]+',' ', s.replace('\n',' '))

# ---------- 인라인 렌더 ----------
def esc(s):
    # 표/본문 안에서 마크다운 문법과 충돌하는 문자만 최소 이스케이프
    return s.replace('|','\\|')

def inline(n, in_table=False):
    """노드를 인라인 마크다운 문자열로."""
    if n.tag=='#text':
        return esc(ws(n.text)) if in_table else ws(n.text)
    if n.tag=='br':
        return '<br>' if in_table else '\n'
    if n.tag in ('script','style'): return ''
    parts=[inline(c, in_table) for c in n.children]
    inner=''
    for q in parts:
        if inner and q and not inner[-1].isspace() and not q[0].isspace() \
           and inner[-1] not in '([{‘“「<' \
           and (q[0]=='`' or inner[-1]=='`' or (inner[-1]=='*' and q[0]=='*')):
            inner+=' '
        inner+=q
    stripped=inner.strip()
    if not stripped: return inner
    if n.tag in ('b','strong'):
        if 'mono' in n.cls: return f'`{stripped}`'
        return f'**{stripped}**'
    if n.tag in ('em','i'):
        return f'*{stripped}*'
    if n.tag=='code': return f'`{stripped}`'
    if n.tag=='a':
        href=n.attrs.get('href')
        return f'[{stripped}]({href})' if href and href!='#' else stripped
    if n.tag=='span':
        if 'mono' in n.cls: return f'`{stripped}`'
        if 'thr' in n.cls:  return f'`{stripped}`'        # 임계치 배지
        if n.cls & {'g','w','t'}: return f'**{stripped}**' # Given/When/Then
        return inner
    if n.tag=='small': return inner
    return inner

def itext(n, in_table=False):
    return re.sub(r' {2,}',' ', inline(n, in_table)).strip()

def plain(n):
    if n.tag=='#text': return ws(n.text)
    if n.tag=='br': return ' '
    return ''.join(plain(c) for c in n.children)

def ptext(n): return re.sub(r'\s+',' ', plain(n)).strip()

def rawtext(n):
    """줄바꿈을 보존한 원문 텍스트 (mermaid 등 코드 블록용)"""
    if n.tag=='#text': return n.text
    if n.tag=='br': return '\n'
    return ''.join(rawtext(c) for c in n.children)

# ---------- 블록 렌더 ----------
BLOCK_TAGS={'div','section','table','p','ul','ol','li','h1','h2','h3','h4','pre','header','main','article','figure','dl','dt','dd'}

def is_block(n):
    return n.tag in BLOCK_TAGS

def render_table(n, out):
    rows=[]
    def walk(x):
        if x.tag=='tr':
            cells=[c for c in x.children if c.tag in ('td','th')]
            rows.append((x, cells)); return
        for c in x.children: walk(c)
    walk(n)
    if not rows: return
    header=None; body=[]
    for tr,cells in rows:
        vals=[itext(c, True) or ' ' for c in cells]
        # colspan 보정
        exp=[]
        for c,v in zip(cells, vals):
            exp.append(v)
            for _ in range(int(c.attrs.get('colspan',1))-1): exp.append(' ')
        if header is None and all(c.tag=='th' for c in cells):
            header=exp
        else:
            body.append(exp)
    width=max([len(header)] if header else [0]+[0])
    width=max(width, max((len(r) for r in body), default=0))
    if header is None:
        header=['']*width
    header=header+['']*(width-len(header))
    out.append('| ' + ' | '.join(header) + ' |')
    out.append('|' + '|'.join([' --- ']*width) + '|')
    for r in body:
        r=r+[' ']*(width-len(r))
        out.append('| ' + ' | '.join(x if x.strip() else ' ' for x in r) + ' |')
    out.append('')

def render_h3div(n, out):
    em=[c for c in n.children if c.tag=='em']
    b =[c for c in n.children if c.tag in ('b','strong')]
    sp=[c for c in n.children if c.tag=='span']
    num=ptext(em[0]) if em else ''
    ttl=ptext(b[0]) if b else ''
    note=' · '.join(ptext(s) for s in sp if ptext(s))
    if not (num or ttl):
        out.append(f'### {itext(n)}'); out.append('')
        return
    out.append(f'### {(num+" "+ttl).strip()}')
    out.append('')
    if note:
        out.append(f'*{note}*'); out.append('')

def blockquote(lines):
    res=[]
    for l in lines:
        res.append(('> '+l).rstrip() if l.strip() else '>')
    return res

def render_card(n, out):
    buf=[]
    render_children(n, buf)
    while buf and not buf[-1].strip(): buf.pop()
    while buf and not buf[0].strip(): buf.pop(0)
    if not buf: return
    out.extend(blockquote(buf)); out.append('')

def render_story(n, out):
    sh=find_cls(n,'sh'); sb=find_cls(n,'sb') or find_cls(n,'sb2')
    if sh is None: sh=find_cls(n,'sh2')
    if sh is not None:
        idn=find_cls(sh,'id'); txt=find_cls(sh,'txt')
        if idn is not None:
            out.append(f'#### {itext(idn)}'); out.append('')
        if txt is not None:
            out.append(itext(txt)); out.append('')
    if sb is not None:
        render_children(sb, out)

def render_ac(n, out):
    for item in n.children:
        if item.tag!='div': continue
        i2=find_cls(item,'id2'); bd=find_cls(item,'body')
        if i2 is not None and bd is not None:
            body=re.sub(r'\s*\n\s*',' ', itext(bd))
            out.append(f'- **{itext(i2)}** — {body}')
        else:
            sub=[]; render_children(item, sub)
            for l in sub:
                if l.strip(): out.append('- '+l if not l.startswith(('-','>','|','#')) else l)
    out.append('')

def find_cls(n, c):
    for ch in n.children:
        if c in ch.cls: return ch
    for ch in n.children:
        r=find_cls(ch,c)
        if r is not None: return r
    return None

def render_children(n, out):
    inline_buf=[]
    def flush():
        if inline_buf:
            s=re.sub(r' {2,}',' ',''.join(inline_buf)).strip()
            if s: out.append(s); out.append('')
            inline_buf.clear()
    for c in n.children:
        if c.tag in ('script','style'): continue
        if c.tag=='#text':
            if c.text.strip(): inline_buf.append(ws(c.text))
            elif inline_buf and not inline_buf[-1].endswith(' '): inline_buf.append(' ')
            continue
        if is_block(c) or c.tag=='pre':
            flush(); render_block(c, out)
        else:
            inline_buf.append(inline(c))
    flush()

def render_block(n, out):
    cls=n.cls
    if n.tag=='pre' or 'mermaid' in cls:
        code=rawtext(n)
        lines=[l.rstrip() for l in code.split('\n')]
        while lines and not lines[0].strip(): lines.pop(0)
        while lines and not lines[-1].strip(): lines.pop()
        ind=min([len(l)-len(l.lstrip()) for l in lines if l.strip()] or [0])
        code='\n'.join(l[ind:] if l.strip() else '' for l in lines)
        out.append('```mermaid'); out.extend(code.split('\n')); out.append('```'); out.append('')
        return
    if n.tag=='table':
        render_table(n, out); return
    if n.tag=='h1':
        out.append('# '+itext(n).replace('\n',' ')); out.append(''); return
    if n.tag=='h2':
        out.append('## '+itext(n).replace('\n',' ')); out.append(''); return
    if n.tag in ('h3','h4'):
        out.append('#### '+itext(n).replace('\n',' ')); out.append(''); return
    if n.tag=='dl':
        pending=None
        for ch in n.children:
            if ch.tag=='dt':
                if pending is not None: out.append(f'- **{pending}**')
                pending=itext(ch)
            elif ch.tag=='dd':
                dd=re.sub(r'\s*\n\s*',' ', itext(ch))
                lead=f'**{pending}** — ' if pending else ''
                out.append('- '+lead+dd); pending=None
        if pending is not None: out.append(f'- **{pending}**')
        out.append(''); return
    if n.tag in ('dt','dd'):
        t=itext(n)
        if t: out.append(t); out.append('')
        return
    if n.tag in ('ul','ol'):
        i=0
        for li in n.children:
            if li.tag!='li': continue
            i+=1
            mark='- ' if n.tag=='ul' else f'{i}. '
            sub=[]; render_children(li, sub)
            sub=[l for l in sub if l.strip()]
            if not sub: continue
            out.append(mark+sub[0])
            for l in sub[1:]: out.append('  '+l)
        out.append(''); return
    if 'h3' in cls:
        render_h3div(n, out); return
    if 'rh' in cls and n.tag=='div':
        em=[c for c in n.children if c.tag=='em']
        b =[c for c in n.children if c.tag in ('b','strong')]
        sp=[c for c in n.children if c.tag=='span']
        head=' · '.join(x for x in [ptext(em[0]) if em else '', ptext(b[0]) if b else ''] if x)
        lvl=' · '.join(ptext(x) for x in sp if ptext(x))
        out.append(f'**{head}**' + (f' — {lvl}' if lvl else ''))
        out.append('')
        return
    if 'story' in cls:
        render_story(n, out); return
    if 'ac' in cls:
        render_ac(n, out); return
    if cls & {'eyebrow','knum'}:
        t=itext(n)
        if t: out.append(f'**{t}**'); out.append('')
        return
    if 'badge' in cls:
        t=itext(n)
        if t: out.append(f'`{t}`'); out.append('')
        return
    if cls & {'card','xbox','warn','risk','mit','ev','sec','cap'} and n.tag=='div':
        render_card(n, out); return
    if n.tag=='div':
        kids=[c for c in n.children if c.tag not in ('#text','br')]
        if len(kids)==2 and 'k' in kids[0].cls and 'v' in kids[1].cls:
            out.append(f'- **{itext(kids[0])}** — {itext(kids[1])}')
            return
    if 'k' in cls and n.tag=='div':
        t=itext(n)
        if t: out.append(f'**{t}**'); out.append('')
        return
    if n.tag=='p':
        t=itext(n)
        if t: out.append(t); out.append('')
        return
    render_children(n, out)

# ---------- 실행 ----------
raw=open(SRC, encoding='utf-8').read()
raw=re.sub(r'<!--.*?-->','',raw,flags=re.S)
bld=Builder(); bld.feed(raw)

def collect(n, tag, acc):
    if n.tag==tag: acc.append(n)
    for c in n.children: collect(c, tag, acc)
    return acc

body=collect(bld.root,'body',[])[0]
slides=[s for s in collect(body,'section',[]) if 'slide' in s.cls]
title=ptext(collect(bld.root,'title',[])[0])

doc=[]
doc.append(f'# {title}')
doc.append('')
doc.append('> 원본 `docs/source-docs/[PRD]AI-Place-Mate-PRD-v0_1.html` 을 내용 손실 없이 Markdown으로 변환한 문서입니다.')
doc.append('> 원본은 15장 슬라이드 덱이며, 각 슬라이드를 `---` 로 구분했습니다.')
doc.append('> 표·mermaid 다이어그램·수용 기준 임계치는 원문 값을 그대로 보존했습니다.')
doc.append('')

for i,s in enumerate(slides, 1):
    doc.append('---')
    doc.append('')
    doc.append(f'<!-- 슬라이드 {i:02d} / {len(slides)} -->')
    doc.append('')
    buf=[]
    render_children(s, buf)
    # 연속 빈 줄 정리
    clean=[]
    for l in buf:
        if not l.strip() and clean and not clean[-1].strip(): continue
        clean.append(l.rstrip())
    while clean and not clean[-1].strip(): clean.pop()
    # 리스트 블록 뒤에 빈 줄 보장
    fixed=[]
    for j,l in enumerate(clean):
        fixed.append(l)
        if l.startswith('- ') and j+1<len(clean):
            nx=clean[j+1]
            if nx.strip() and not nx.startswith(('- ','  ')): fixed.append('')
    doc.extend(fixed); doc.append('')

# HUD 등 슬라이드 밖 UI 요소는 문서 내용이 아니므로 제외
text='\n'.join(doc)
text=re.sub(r'\n{4,}','\n\n\n',text)
open(OUT,'w',encoding='utf-8').write(text.rstrip()+'\n')
print(f'슬라이드 {len(slides)}장 → {OUT} ({len(text.splitlines())} lines)')
