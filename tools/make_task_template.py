#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub Project 용 TASK 템플릿 생성 스크립트.

`.github/ISSUE_TEMPLATE/feature-task.md` 를 생성한다. 재실행하면 덮어쓴다.

사용법:
    python3 tools/make_task_template.py            # 기본 경로에 생성
    python3 tools/make_task_template.py --stdout   # 파일로 쓰지 않고 출력만
"""
import sys, os

OUT = ".github/ISSUE_TEMPLATE/feature-task.md"

TEMPLATE = """---
name: GitHub Project 용 TASK 템플릿
about: SRS 기반의 구체적인 개발 태스크 명세
title: "[Feature] <TASK-ID>: {기능 요약}"
labels: 'feature'
assignees: ''
---

<!--
  GitHub Project 용 TASK 템플릿 · TASK-AIPLACE-MVP-001 기준

  라벨 규약 (이슈 생성 후 추가)
    관점   part:backend | part:frontend | part:infra | part:design
    도메인 epic:INF | epic:TEC | epic:DAT | epic:QRY | epic:EVD | epic:RNK
           epic:RSV | epic:MCH | epic:AGR | epic:ANA | epic:SEC | epic:REL | epic:UX
    복잡도 complexity:H | complexity:M | complexity:L
    단계   sprint:S-1 ~ sprint:S8
  꺾쇠(<>)와 중괄호({}) 표시는 전부 실제 값으로 바꾸고 삭제할 것.
-->

## 🎯 Summary
- 기능명: [<TASK-ID>] <Feature 기능명 — 태스크 리스트의 표기와 동일하게>
- 목적: <이 태스크가 없으면 무엇이 성립하지 않는지를 한 문장으로>

## 🔗 References (Spec & Context)
> 💡 AI Agent & Dev Note: 작업 시작 전 아래 문서를 반드시 먼저 Read/Evaluate 할 것.
- 태스크 리스트: `/docs/[태스크 리스트] AI-Place-Mate.md#<task-anchor>`
- SRS 문서(기술제약 반영판): `/docs/[SRS 문서] AI-Place-Mate (기술제약 반영판).md#<req-anchor>`
- SRS 문서(기술 중립판): `/docs/[SRS 문서] AI-Place-Mate (한글).md#<req-anchor>`
- 설계 문서(SDD): `/docs/[설계 문서] AI-Place-Mate (한글).md#<diagram-anchor>`
- 시퀀스 다이어그램: `<SD-01 ~ SD-10 중 해당 항목 · 없으면 "해당 없음">`
- 데이터 모델 (ERD): `/docs/[설계 문서] AI-Place-Mate (한글).md#31-erd--개체와-관계`
- 서버 진입점 명세: `/docs/[SRS 문서] AI-Place-Mate (기술제약 반영판).md#61-서버-진입점-목록`

## ✅ Task Breakdown (실행 계획)
<!-- 각 항목은 하루 안에 끝나는 크기로. 완료 여부를 보는 사람이 판단할 수 있게 -->
- [ ] <실행 단계 1>
- [ ] <실행 단계 2>
- [ ] <실행 단계 3>
- [ ] <단위 테스트 작성>
- [ ] <통합 지점 검증>

## 🧪 Acceptance Criteria (BDD/GWT)
<!-- SRS §9 수용 기준에서 가져오고, 없으면 요구사항의 인수 기준을 GWT로 옮길 것.
     정상 흐름 1개 이상 + 실패 흐름 1개 이상을 반드시 포함한다 (SRS §9 규약) -->

Scenario 1: <정상 흐름 제목>
- Given: <사전 조건>
- When: <행위>
- Then: <결과 + 측정 가능한 임계치>

Scenario 2: <실패 흐름 제목>
- Given: <실패를 유발하는 사전 조건>
- When: <행위>
- Then: <열화 동작 + 임계치. "빈 화면 금지" 규칙 위반이 없어야 한다>

## ⚙️ Technical & Non-Functional Constraints
<!-- 해당하는 것만 남기고 나머지는 삭제. 수치는 SRS §4.2에서 그대로 가져올 것 -->
- 성능: <REQ-NF-001a 결정론 경로 p95 ≤ 1,000ms / REQ-NF-001b LLM 경로 p95 ≤ 2,500ms 등>
- 안정성: <REQ-NF-006 5xx ≤ 0.3% (결제 ≤ 0.1%) 등>
- 보안·개인정보: <REQ-NF-010 · 011 · 012 중 해당 항목>
- 비용: <REQ-NF-013 세션당 추론 비용 ≤ 12원 등>
- 기술 제약: <C-TEC-001 ~ 007 및 파생 규범 D-01 ~ D-08 중 이 태스크를 구속하는 항목>

## 🏁 Definition of Done (DoD)
- [ ] 모든 Acceptance Criteria를 충족하는가?
- [ ] 단위 테스트(Unit Test) 및 통합 테스트(Integration Test)가 추가되었고 통과하는가?
- [ ] 정적 분석 경고가 없는가? <!-- 본 프로젝트: tsc --noEmit · ESLint · verify-constraints.mjs (REQ-TEC-012) -->
- [ ] 인터페이스 명세가 최신화되었는가? <!-- 본 프로젝트: SRS §6.1 서버 진입점 목록 · §6.2 Prisma 스키마 -->
- [ ] Vercel 프리뷰 배포가 성공했는가? <!-- 빌드 실패 = 배포 차단 (C-TEC-007 · ADR-T08) -->
- [ ] 관련 계측 이벤트가 적재되는가? <!-- 해당 시 · SRS §10.2 -->

## 🚧 Dependencies & Blockers
- Depends on: #<이슈번호> (<선행 TASK-ID> — 태스크 리스트의 선행 태스크와 일치해야 함)
- Blocks: #<이슈번호> (<후행 TASK-ID>)
- External Blocker: <DEP-T1 ~ T5 등 외부 의존성 · 없으면 "없음">
"""


def main():
    if "--stdout" in sys.argv:
        sys.stdout.write(TEMPLATE)
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(TEMPLATE)
    lines = TEMPLATE.count("\n")
    print(f"생성: {OUT} ({lines}줄)")
    print("제목: GitHub Project 용 TASK 템플릿")
    return 0


if __name__ == "__main__":
    sys.exit(main())
