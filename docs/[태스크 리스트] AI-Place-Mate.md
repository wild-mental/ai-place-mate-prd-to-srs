# [태스크 리스트] AI-Place-Mate

**문서 ID:** TASK-AIPLACE-MVP-001

**개정 버전:** 3.0 (축약 적용 — 118 → 56건)

**날짜:** 2026-08-25

**근거 문서:** SRS-AIPLACE-TEC-001 v1.0 (`[SRS 문서] AI-Place-Mate (기술제약 반영판).md`)

**참조 문서:** SRS-AIPLACE-MVP-001 (기술 중립판) · SDD-AIPLACE-MVP-001 (설계 문서) · ANL-AIPLACE-TASK-001 (방법론 적합성 평가)

> ⚙️ **이 문서는 생성물이다.** 단일 원천은 `tools/tasks_data.py` 이며 `python3 tools/gen_task_list.py` 로 재생성한다. **직접 편집하지 말 것** — `후행 태스크(Blocks)` 는 `선행 태스크` 에서 자동 역산되므로 수기 편집은 반드시 불일치를 만든다.

---

## 0. 이 문서를 읽는 법

### 0.1 근거와 범위

본 태스크 리스트는 **기술제약 반영판 SRS**를 기준으로 작성했다. 기술 중립판이 아니라 반영판을 택한 이유는, 반영판만이 구현 단위(Server Action · Route Handler · RSC · Cron)를 확정하고 있어 **실행 가능한 태스크로 분해할 수 있기 때문**이다.

- SRS에 **명시되지 않은 기능은 추가하지 않았다.** 모든 태스크는 `관련 SRS 섹션` 열로 원문을 지목한다.
- 요구사항 ID는 두 SRS가 공유하므로, `REQ-FUNC-006` 같은 참조는 양쪽에서 동일하게 성립한다.
- 연기 대상(SRS §14.3)은 **태스크로 만들지 않았다.** 제외 내역은 부록 D에 있다.

### 0.2 관점 분리

| Part | 관점 | ID 접두어 | 산출물 성격 |
| --- | --- | --- | --- |
| **Part A** | 백엔드 · 프론트엔드 개발 및 인프라 구성 | `INF` `TEC` `CTR` `DAT` `MCK` `QRY` `EVD` `RNK` `RSV` `MCH` `AGR` `ANA` `SEC` `REL` `TST` | 동작하는 코드 · 구성 |
| **Part B** | UI/UX 디자인 | `UX` | 화면 정의 · 디자인 산출물 |

Part A 안에서도 **UX 구현(6건 · 유형 `UI`)과 기능 구현(BE)을 분리**한다. 담당자와 리뷰 관점이 다르고, UX 구현 진척을 독립적으로 추적해야 하기 때문이다. 병합 시에도 두 계층을 섞지 않는다(원칙 P6 · ANL-AIPLACE-TASK-002 §4.4).

### 0.3 유형(Type) 분류

`유형` 열은 태스크가 추출 방법론의 어느 단계에 속하는지를 나타낸다. Read/Write 구분은 SRS §6.1의 구현 단위(RSC 조회 = Read / Server Action · Cron · 웹훅 = Write)를 따른다.

| 유형 | 의미 | 방법론 단계 | 건수 |
| --- | --- | --- | --- |
| `Contract` | DTO · 스키마 · 에러 코드 등 공유 계약 | Step 1 | 3 |
| `Data` | DB 스키마 · 정규화 사전 · Mock 픽스처 | Step 1 | 3 |
| `Read` | 조회 · 질의 경로 (상태 변경 없음) | Step 2 | 5 |
| `Write` | 상태 변경 · Server Action · Cron · 웹훅 | Step 2 | 12 |
| `UI` | **프론트엔드 화면·클라이언트 구현** — 기능 구현(BE)과 분리 | Step 2 | 6 |
| `Test` | AC를 실행 가능한 테스트로 변환 | Step 3 | 6 |
| `Infra` | 프레임워크 · 배포 · 게이트 · 외부 연동 배선 | Step 4 | 6 |
| `NFR` | 보안 · 관측 · 비용 · 복구 | Step 4 | 7 |
| `Design` | 디자인 토큰 · 화면 정의 | — | 8 |
| | | **합계** | **56** |

### 0.4 Epic 목록

| Epic | 도메인 | 태스크 수 |
| --- | --- | --- |
| `INF` | Platform & Infra | 4 |
| `TEC` | Constraint Gate | 1 |
| `CTR` | Contract | 3 |
| `DAT` | Data & Indexing | 4 |
| `MCK` | Mock | 1 |
| `QRY` | Query & Parsing | 5 |
| `EVD` | Evidence | 3 |
| `RNK` | Ranking | 2 |
| `RSV` | Reservation & Payment | 3 |
| `MCH` | Merchant Console | 4 |
| `AGR` | Agent Room | 5 |
| `ANA` | Analytics | 3 |
| `SEC` | Security & Privacy | 2 |
| `REL` | Reliability & Ops | 2 |
| `TST` | Test | 6 |
| `UX` | UI/UX Design | 8 |
| | **합계** | **56** |

### 0.5 복잡도 판정 기준

| 등급 | 기준 | 예 |
| --- | --- | --- |
| **H** | 외부 시스템 연동, 새 개념 도입, 되돌림 비용이 크거나 SRS가 임계치를 건 항목 | PG 웹훅 멱등 처리 · 2단 파싱 · RLS 정책 |
| **M** | 기존 패턴의 조합. 설계는 정해져 있고 구현량이 있음 | Server Action 작성 · Cron 엔드포인트 |
| **L** | 설정·선언 수준. 판단이 거의 필요 없음 | 환경 변수 등록 · PITR 활성화 |

분포: **H 21 · M 34 · L 1**

---

## Part A. 백엔드 · 프론트엔드 개발 및 인프라 구성

### A-1. Epic `INF` — Platform & Infra

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="INF-001"></a>**INF-001** | Platform & Infra | Next.js 앱 생성 · Vercel 연결 · 환경 변수 · Cron 스케줄 | `Infra` | §1.5 C-TEC-001 · §14.1 디렉터리 구조 · §1.5 C-TEC-007 · §14.4 · §6.5 환경 변수 · §6.1 Cron 스케줄 · §4.3 REQ-TEC-013 | None | AGR-005 · ANA-002 · DAT-010 · INF-002 · INF-003 · INF-008 · MCK-001 · QRY-002 · REL-001 · RSV-003 · RSV-005 · SEC-001 · TEC-001 | M |
| <a id="INF-002"></a>**INF-002** | Platform & Infra | Tailwind CSS + shadcn/ui 설정 및 네이버 지도 탭 진입 경로 | `UI` | §1.5 C-TEC-004 · §4.3 REQ-TEC-007 · §3.2 인터페이스 목록 · ADR-005 | INF-001 · UX-001 | MCH-002 | M |
| <a id="INF-003"></a>**INF-003** | Platform & Infra | Supabase · Prisma 연결 (Supavisor) 및 마이그레이션 승인 절차 | `Infra` | §1.5 C-TEC-003 · §4.3 REQ-TEC-006 · §6.4 · §4.3 REQ-TEC-004 · §4.3 REQ-TEC-005 · ADR-T04 · §14.4 배포 파이프라인 | INF-001 | AGR-002 · DAT-001 · MCH-001 · REL-001 · REL-004 · TEC-001 | M |
| <a id="INF-008"></a>**INF-008** | Platform & Infra | `proxy.ts` 요청 태깅 및 인증 훅 | `Infra` | §3.1 배포 토폴로지 · §3.3 | INF-001 | None | M |

### A-2. Epic `TEC` — Constraint Gate

> 제약은 선언이고, 이 Epic은 **선언을 어겼을 때 빌드가 실패하게 만드는 장치**다. S-1에서 먼저 작동시켜야 이후 스프린트의 위반이 즉시 드러난다(SRS §14.2).

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="TEC-001"></a>**TEC-001** | Constraint Gate | 제약 게이트 구축 — 모듈 스캐폴딩 · 공개 표면 · 경계 규칙 · 검사 스크립트 · 빌드 편입 | `Infra` | §3.3 모듈 구조 · §14.1 · §4.3 REQ-TEC-002 · ADR-T01 · §4.3 REQ-TEC-001 · 003 · 004 · 005 · 008 · 011 · 015 · §4.3 REQ-TEC-012 · §14.4 · ADR-T08 | INF-001 · INF-003 | TST-007 · TST-008 | H |

### A-3. Epic `CTR` — Contract

> **Step 1 계약 태스크.** 백엔드와 프론트엔드가 공유하는 기준점이다. 계약이 기능 태스크 안에 묻혀 있으면 두 태스크가 같은 계약을 다르게 구현해도 탐지되지 않는다.

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="CTR-001"></a>**CTR-001** | Contract | Server Action 9종 입출력 계약 (Zod DTO) 및 `ConditionSet` 스키마 | `Contract` | §6.1 Server Actions · §6.6 AI 호출 규약 · §4.3 REQ-TEC-010 | DAT-001 | AGR-001 · CTR-002 · EVD-005 · MCH-004 · MCK-001 · QRY-001 · QRY-002 · QRY-005 · QRY-007 · RSV-001 · TST-001 · TST-005 | H |
| <a id="CTR-002"></a>**CTR-002** | Contract | Route Handler 8종 요청·응답 계약 및 에러 코드 체계 | `Contract` | §6.1 Route Handlers · §6.1 · §6.3-6 빈 화면 금지 | CTR-001 | ANA-002 · EVD-004 · MCK-001 · RNK-003 · RSV-003 · TST-004 | M |
| <a id="CTR-005"></a>**CTR-005** | Contract | 계측 이벤트 계약 20종 (필수 속성 포함) | `Contract` | §10.2 계측 구현 | DAT-001 | ANA-002 · TST-008 | H |

### A-4. Epic `DAT` — Data & Indexing

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="DAT-001"></a>**DAT-001** | Data & Indexing | Prisma 스키마 전체 — 엔터티 · Verification · Event 파티셔닝 · `canonicalKey` 정규화 사전 | `Data` | §6.2 · §4.1 REQ-FUNC-001 · 010 · §4.1 REQ-FUNC-007 · 009 · §10.2 계측 구현 · 003 | INF-003 | AGR-001 · AGR-002 · CTR-001 · CTR-005 · DAT-006 · DAT-008 · DAT-010 · EVD-001 · MCH-003 · MCH-004 · QRY-009 · RSV-001 · RSV-003 · SEC-001 · TST-008 | H |
| <a id="DAT-006"></a>**DAT-006** | Data & Indexing | 색인 파이프라인 및 `use cache` 계층 | `Write` | §4.1 REQ-FUNC-001 · ADR-001 · §4.2 REQ-NF-002 · ADR-T05 | DAT-001 | QRY-001 · QRY-007 · QRY-009 | H |
| <a id="DAT-008"></a>**DAT-008** | Data & Indexing | RLS 정책 및 `audit_logs` 트리거 | `NFR` | §6.4 · §4.2 REQ-NF-012 | DAT-001 | MCH-001 · TST-008 | H |
| <a id="DAT-010"></a>**DAT-010** | Data & Indexing | 신선도 스캔 Cron 및 재확인 큐 | `Write` | §6.1 · §4.2 REQ-NF-008 | DAT-001 · INF-001 | EVD-005 | M |

### A-5. Epic `MCK` — Mock

> **Step 1 Mock 태스크.** UI 작업이 백엔드 완성을 기다리지 않게 한다. SRS의 '빈 화면 금지'·'근거 없는 후보 반환 금지'가 요구하는 **실패·경계 상태**는 픽스처가 있어야 만들 수 있다.

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="MCK-001"></a>**MCK-001** | Mock | 도메인 픽스처 세트 (Top-3 · 파싱 · 대화방 · 결제) 및 Mock 모드 스위치 | `Data` | §6.3-2 · §4.1 REQ-FUNC-006 · §4.2.1 · §4.1 REQ-FUNC-004 · §9.3 · §4.1 REQ-FUNC-009 · §9.2 · §4.1 REQ-FUNC-007 · §6.5 환경 변수 | CTR-001 · CTR-002 · INF-001 | TST-001 · TST-004 · TST-005 | M |

### A-6. Epic `QRY` — Query & Parsing

> **2단 파싱이 이 Epic의 핵심**이다(ADR-T02). 결정론 파서가 질의의 70% 이상을 흡수하지 못하면 응답 시간(REQ-NF-001a)과 추론 비용(REQ-NF-013)이 동시에 무너진다.

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="QRY-001"></a>**QRY-001** | Query & Parsing | 결정론 파서 · 조건 카테고리 사전 · 파싱 캐시 | `Read` | §4.2.1 · §4.1 REQ-FUNC-004 · ADR-T02 · §4.2 REQ-NF-002b | CTR-001 · DAT-006 | QRY-005 | H |
| <a id="QRY-002"></a>**QRY-002** | Query & Parsing | AI SDK 단일 진입점 `lib/ai.ts` 및 Gemini 폴백 파서 | `Infra` | §6.6 · §4.3 REQ-TEC-008 · 009 · 010 · ADR-T10 · §4.1 REQ-FUNC-004 · §1.5 C-TEC-005 · 006 | CTR-001 · INF-001 | ANA-007 · EVD-001 · QRY-005 · SEC-002 | H |
| <a id="QRY-005"></a>**QRY-005** | Query & Parsing | `submitQuery` Server Action 및 `parse_path` 경로 태깅 | `Write` | §6.1 Server Actions · §9.1 · §9.1 계측 필수 사항 · §10.1 | ANA-002 · CTR-001 · QRY-001 · QRY-002 | REL-001 · RNK-003 | M |
| <a id="QRY-007"></a>**QRY-007** | Query & Parsing | 인당 가격대 필터 · 예상가 추정 · `submitPriceFeedback` | `Read` | §4.1 REQ-FUNC-002 · §6.1 | CTR-001 · DAT-006 | RNK-001 | M |
| <a id="QRY-009"></a>**QRY-009** | Query & Parsing | 메뉴명 질의 해석 및 유사 메뉴·반경 확대 폴백 | `Read` | §4.1 REQ-FUNC-003 · §6.3-6 | DAT-001 · DAT-006 | RNK-001 | M |

### A-7. Epic `EVD` — Evidence

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="EVD-001"></a>**EVD-001** | Evidence | 근거 조립 · 4항목 검증 · 90일 경고 · 판정형 문구 필터 | `Read` | §4.1 REQ-FUNC-005 · ADR-002 · §6.3-2 · 5 · §6.3-4 · §6.6 프롬프트 규약 | DAT-001 · QRY-002 | EVD-004 · EVD-005 · RNK-001 | H |
| <a id="EVD-004"></a>**EVD-004** | Evidence | 공유 카드 OG 이미지 Route Handler (`next/og`) | `UI` | §6.1 · §4.1 REQ-FUNC-005 | CTR-002 · EVD-001 · UX-010 | None | M |
| <a id="EVD-005"></a>**EVD-005** | Evidence | `reportMismatch` Server Action (재확인 큐 연동) | `Write` | §6.1 · §4.1 REQ-FUNC-005 | CTR-001 · DAT-010 · EVD-001 | None | M |

### A-8. Epic `RNK` — Ranking

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="RNK-001"></a>**RNK-001** | Ranking | 근거 미충족 후보 배제 · Top-3 고정 선정 · 비교 축 생성 | `Read` | §4.1 REQ-FUNC-006 · §6.3-2 · 3 · ADR-003 | EVD-001 · QRY-007 · QRY-009 | RNK-003 | H |
| <a id="RNK-003"></a>**RNK-003** | Ranking | 결과 RSC 스트리밍 페이지 및 구조화 필터 폴백 화면 | `UI` | §9.1 · §4.2 REQ-NF-001a · 001b · §4.2 REQ-NF-007 · §6.3-6 | CTR-002 · QRY-005 · RNK-001 · UX-003 · UX-004 · UX-006 | AGR-006 · RSV-001 · TST-010 | H |

### A-9. Epic `RSV` — Reservation & Payment

> SRS §14.1에 따라 **REQ-FUNC-007은 REQ-FUNC-006과 DEP-01(PG 계약)에 선행 종속**하며, 가맹 콘솔·대화방보다 **먼저** 착수한다.

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="RSV-001"></a>**RSV-001** | Reservation & Payment | `selectProposal` 조건 승계 및 주문량 금액 산출 | `Write` | §6.1 · §4.1 REQ-FUNC-007 | CTR-001 · DAT-001 · RNK-003 | RSV-003 | M |
| <a id="RSV-003"></a>**RSV-003** | Reservation & Payment | `requestPayment` Server Action 및 PG 웹훅 (서명·멱등) | `Write` | §6.1 · §4.2 REQ-NF-011 · DEP-T4 · §9.2 · §15-9 | CTR-002 · DAT-001 · INF-001 · RSV-001 · UX-015 | RSV-005 | H |
| <a id="RSV-005"></a>**RSV-005** | Reservation & Payment | `cancelReservation` 환불 및 노쇼 판정 Cron | `Write` | §6.1 · §4.1 REQ-FUNC-007 | INF-001 · RSV-003 | MCH-003 | M |

### A-10. Epic `MCH` — Merchant Console

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="MCH-001"></a>**MCH-001** | Merchant Console | Supabase Auth 연동 및 MFA 적용 | `Infra` | §4.2 REQ-NF-012 · §3.2 | DAT-008 · INF-003 | MCH-002 | H |
| <a id="MCH-002"></a>**MCH-002** | Merchant Console | `(merchant)` 라우트 그룹 및 전용 레이아웃 분리 | `UI` | §14.1 · §8 사용자 특성 | INF-002 · MCH-001 · UX-013 | MCH-004 | M |
| <a id="MCH-003"></a>**MCH-003** | Merchant Console | 매장 프로필·수용 조건 스키마 및 매칭기 | `Data` | §6.2 · §4.1 REQ-FUNC-008 | DAT-001 · RSV-005 | AGR-001 · MCH-004 | M |
| <a id="MCH-004"></a>**MCH-004** | Merchant Console | `saveMerchantProfile` Server Action 및 EvidenceGuard | `Write` | §6.1 · §4.1 REQ-FUNC-008 · §6.3-2 | CTR-001 · DAT-001 · MCH-002 · MCH-003 | AGR-003 | M |

### A-11. Epic `AGR` — Agent Room

> 대화방은 **서버 프로세스 없이** 구현한다 — DB 상태 + Realtime + lazy close(ADR-T06). 마감 정확도가 Cron 주기에 종속되지 않아야 한다(SRS §9.3).

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="AGR-001"></a>**AGR-001** | Agent Room | `createAgentRoom` Server Action 및 에이전트 3–5곳 소환 | `Write` | §6.1 · §4.1 REQ-FUNC-009 · §9.3 | CTR-001 · DAT-001 · MCH-003 | AGR-003 · AGR-005 | H |
| <a id="AGR-002"></a>**AGR-002** | Agent Room | Supabase Realtime 클라이언트 및 대화방 채널 구독 | `UI` | §3.2 · §9.3 · ADR-T06 | DAT-001 · INF-003 | AGR-005 | H |
| <a id="AGR-003"></a>**AGR-003** | Agent Room | `submitProposal` · 적합도 정렬 · 불이행 소환 가중치 하향 | `Write` | §6.1 · §4.1 REQ-FUNC-009 · §6.3-7 · §6.3-10 | AGR-001 · MCH-004 · UX-014 | None | M |
| <a id="AGR-005"></a>**AGR-005** | Agent Room | 마감 판정 — lazy close + 보조 Cron | `Write` | §9.3 · §6.1 · §15-6 | AGR-001 · AGR-002 · INF-001 | AGR-006 | H |
| <a id="AGR-006"></a>**AGR-006** | Agent Room | 유효 제안 0건 시 제안 없는 Top-3 복귀 화면 | `UI` | §6.3-6 · §4.1 REQ-FUNC-009 | AGR-005 · RNK-003 | None | M |

### A-12. Epic `ANA` — Analytics

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="ANA-002"></a>**ANA-002** | Analytics | 이벤트 수집 (`sendBeacon` · `after()`) 및 지표 집계 Cron | `Write` | §6.1 · §10.2 · ADR-T07 · §10.1 성과 지표 | CTR-002 · CTR-005 · INF-001 | ANA-005 · ANA-007 · QRY-005 | H |
| <a id="ANA-005"></a>**ANA-005** | Analytics | 계측 품질 점검 및 임계 알림 디스패처 | `NFR` | §10.2 · §10.3 · §4.2 REQ-NF-015 | ANA-002 | REL-001 | M |
| <a id="ANA-007"></a>**ANA-007** | Analytics | AI 추론 비용 집계 및 단위 경제 리포트 | `NFR` | §4.2 REQ-NF-013 · §10.3 · §4.2 REQ-NF-014 · §10.1 | ANA-002 · QRY-002 | None | M |

### A-13. Epic `SEC` — Security & Privacy

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="SEC-001"></a>**SEC-001** | Security & Privacy | 개인정보 30일 파기 Cron (`/api/cron/purge`) | `NFR` | §6.1 · §4.2 REQ-NF-010 | DAT-001 · INF-001 | None | M |
| <a id="SEC-002"></a>**SEC-002** | Security & Privacy | 프롬프트 개인정보 배제 검증 | `NFR` | §6.6 · §4.2 REQ-NF-010 | QRY-002 | None | M |

### A-14. Epic `REL` — Reliability & Ops

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="REL-001"></a>**REL-001** | Reliability & Ops | 관측 연동 · Cron 실패·풀 사용률 알림 · 롤백 절차 | `NFR` | §10.3 · §4.2 REQ-NF-001a · 001b · §11.2 R-T3 · §11.2 R-T2 · §11.2 R-T4 · §4.2 REQ-NF-009 | ANA-005 · INF-001 · INF-003 · QRY-005 | None | M |
| <a id="REL-004"></a>**REL-004** | Reliability & Ops | Supabase PITR 활성화 (RPO ≤ 5분) | `NFR` | §6.4 · §4.2 REQ-NF-009 | INF-003 | None | L |

### A-15. Epic `TST` — Test

> **Step 3 테스트 태스크.** SRS §9의 인수 기준(AC)을 실행 가능한 테스트 코드 작성 태스크로 변환한 것이다. 여기서 정리된 GWT가 각 Feature 태스크의 DoD 체크리스트로 삽입된다.

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="TST-001"></a>**TST-001** | Test | 수요 측 GWT 테스트 (US-1 ~ US-3) | `Test` | §9.1 US-1 · 중립판 §9.1 · §9.2 · 중립판 §9.2 · 중립판 §9.3 | CTR-001 · MCK-001 | None | M |
| <a id="TST-004"></a>**TST-004** | Test | 결제 GWT 테스트 (US-4) 및 웹훅 멱등성 테스트 | `Test` | §9.2 · 중립판 §9.4 · §4.2 REQ-NF-011 | CTR-002 · MCK-001 | None | M |
| <a id="TST-005"></a>**TST-005** | Test | 공급 측 GWT 테스트 (US-5 · US-6) | `Test` | 중립판 §9.5 · §9.3 · 중립판 §9.6 | CTR-001 · MCK-001 | None | M |
| <a id="TST-007"></a>**TST-007** | Test | 제약 게이트 위반 검증 (의도적 위반 → 빌드 실패) | `Test` | §4.3 REQ-TEC-001 ~ 015 · §14.4 | TEC-001 | None | M |
| <a id="TST-008"></a>**TST-008** | Test | 스키마·정책 검사 테스트 (RLS · 이벤트 계약 · 결제 컬럼 부재) | `Test` | §6.4 · §4.2 REQ-NF-012 · §4.3 REQ-TEC-012 · §10.2 · §4.2 REQ-NF-011 · §6.2 | CTR-005 · DAT-001 · DAT-008 · TEC-001 | None | M |
| <a id="TST-010"></a>**TST-010** | Test | 성능 검증 — 부하 테스트(300 RPS) 및 LCP 측정 | `Test` | §4.2 REQ-NF-001a · 001b · 003 · §10.4 게이트 2 · §4.2 REQ-NF-004 | RNK-003 · UX-003 | None | H |

---

## Part B. UI/UX 디자인

> C-TEC-004에 따라 **shadcn/ui에 존재하는 컴포넌트를 자체 구현하지 않는다**(D-08 · REQ-TEC-007). 따라서 디자인 태스크는 컴포넌트 제작이 아니라 **토큰 정의 · 조합 규칙 · 화면 정의**가 중심이다.

| Task ID | Epic (도메인) | Feature (기능명) | 유형 | 관련 SRS 섹션 | 선행 태스크 (Dependencies) | 후행 태스크 (Blocks) | 복잡도 (H/M/L) |
|---|---|---|---|---|---|---|---|
| <a id="UX-001"></a>**UX-001** | UI/UX Design | 디자인 시스템 — 토큰 · Tailwind 테마 · shadcn/ui 컴포넌트 인벤토리 | `Design` | §1.5 C-TEC-004 · §4.3 REQ-TEC-007 · §1.5.1 D-08 | None | INF-002 · UX-003 · UX-006 · UX-013 · UX-014 · UX-015 | M |
| <a id="UX-003"></a>**UX-003** | UI/UX Design | 조건 입력 화면 · 로딩 스켈레톤 · 모바일 렌더 가이드 | `Design` | §9.2 · §4.1 REQ-FUNC-004 · §4.2 REQ-NF-001b · §4.2 REQ-NF-004 | UX-001 | RNK-003 · TST-010 · UX-004 | M |
| <a id="UX-004"></a>**UX-004** | UI/UX Design | 구조화 필터 폴백 화면 및 빈·오류 상태 정의 | `Design` | §4.2.1 · §4.1 REQ-FUNC-004 · §6.3-6 · §4.2 REQ-NF-007 | UX-003 | RNK-003 | M |
| <a id="UX-006"></a>**UX-006** | UI/UX Design | Top-3 후보 카드 — 근거 4항목 · 90일 경고 · 예상가 범위 · 비교 축 | `Design` | §4.1 REQ-FUNC-005 · 006 · §6.3-2 · §6.3-5 · §4.1 REQ-FUNC-002 · §4.1 REQ-FUNC-006 | UX-001 | RNK-003 · UX-010 | H |
| <a id="UX-010"></a>**UX-010** | UI/UX Design | 공유 카드 비주얼 및 방문 후 입력·신고 폼 | `Design` | §4.1 REQ-FUNC-005 · §6.1 · §4.1 REQ-FUNC-002 · 005 | UX-006 | EVD-004 | M |
| <a id="UX-013"></a>**UX-013** | UI/UX Design | 가맹 콘솔 레이아웃 (설정 화면 ≤ 3개 · 필수 항목 ≤ 5개) | `Design` | §4.1 REQ-FUNC-008 · §8 | UX-001 | MCH-002 | H |
| <a id="UX-014"></a>**UX-014** | UI/UX Design | 대화방 카운트다운 및 제안 비교 화면 | `Design` | §9.3 · §4.1 REQ-FUNC-009 | UX-001 | AGR-003 | H |
| <a id="UX-015"></a>**UX-015** | UI/UX Design | 예약 · 결제 화면 (재입력 필드 0개) | `Design` | §4.1 REQ-FUNC-007 · §9.2 | UX-001 | RSV-003 | M |

---

## 부록 A. 임계 경로 (Critical Path)

**이 그림이 말하는 것:** 어느 태스크가 밀리면 몇 개가 함께 밀리는지다. 괄호 안 숫자는 **직접 후행 태스크 수**(Blocks)이며 전부 자동 역산한 값이다.

```mermaid
flowchart LR
    INF001["INF-001<br/>Next.js 앱 생성 · Vercel <br/>후행 13건"]:::inf
    INF003["INF-003<br/>Supabase · Prisma 연결 (<br/>후행 6건"]:::inf
    DAT001["DAT-001<br/>Prisma 스키마 전체 — 엔터티 · <br/>후행 15건"]:::dat
    CTR001["CTR-001<br/>Server Action 9종 입출력 계<br/>후행 12건"]:::ctr
    DAT006["DAT-006<br/>색인 파이프라인 및 `use cache`<br/>후행 3건"]:::wr
    QRY001["QRY-001<br/>결정론 파서 · 조건 카테고리 사전 · <br/>후행 1건"]:::rd
    RNK001["RNK-001<br/>근거 미충족 후보 배제 · Top-3 고<br/>후행 1건"]:::rd
    RNK003["RNK-003<br/>결과 RSC 스트리밍 페이지 및 구조화 <br/>후행 3건"]:::ui
    RSV003["RSV-003<br/>`requestPayment` Serve<br/>후행 1건"]:::wr
    MCH003["MCH-003<br/>매장 프로필·수용 조건 스키마 및 매칭기<br/>후행 2건"]:::dat
    AGR005["AGR-005<br/>마감 판정 — lazy close + 보<br/>후행 1건"]:::wr
    INF001 --> INF003
    INF003 --> DAT001
    DAT001 --> CTR001
    CTR001 --> DAT006
    DAT006 --> QRY001
    QRY001 --> RNK001
    RNK001 --> RNK003
    RNK003 --> RSV003
    RSV003 --> MCH003
    MCH003 --> AGR005
    classDef ctr fill:#f8d7da,stroke:#dc3545,font-weight:bold
    classDef dat fill:#fff3cd,stroke:#e0a800
    classDef inf fill:#e2e3e5,stroke:#6c757d
    classDef rd fill:#e7f1ff,stroke:#0d6efd
    classDef wr fill:#d1e7dd,stroke:#198754
    classDef tst fill:#ede7f6,stroke:#7e57c2
    classDef nfr fill:#cff4fc,stroke:#0dcaf0
    classDef dsg fill:#fce4ec,stroke:#ec407a
    classDef ui fill:#e0f2f1,stroke:#009688
```

### 후행 태스크가 많은 상위 10건

| 태스크 | Feature | 유형 | 직접 후행 수 | 후행 태스크 |
| --- | --- | --- | --- | --- |
| [`DAT-001`](#DAT-001) | Prisma 스키마 전체 — 엔터티 · Verification · Event 파티셔닝 · `canonicalKey` 정규화 사전 | `Data` | **15** | AGR-001 · AGR-002 · CTR-001 · CTR-005 · DAT-006 · DAT-008 · DAT-010 · EVD-001 · MCH-003 · MCH-004 · QRY-009 · RSV-001 · RSV-003 · SEC-001 · TST-008 |
| [`INF-001`](#INF-001) | Next.js 앱 생성 · Vercel 연결 · 환경 변수 · Cron 스케줄 | `Infra` | **13** | AGR-005 · ANA-002 · DAT-010 · INF-002 · INF-003 · INF-008 · MCK-001 · QRY-002 · REL-001 · RSV-003 · RSV-005 · SEC-001 · TEC-001 |
| [`CTR-001`](#CTR-001) | Server Action 9종 입출력 계약 (Zod DTO) 및 `ConditionSet` 스키마 | `Contract` | **12** | AGR-001 · CTR-002 · EVD-005 · MCH-004 · MCK-001 · QRY-001 · QRY-002 · QRY-005 · QRY-007 · RSV-001 · TST-001 · TST-005 |
| [`UX-001`](#UX-001) | 디자인 시스템 — 토큰 · Tailwind 테마 · shadcn/ui 컴포넌트 인벤토리 | `Design` | **6** | INF-002 · UX-003 · UX-006 · UX-013 · UX-014 · UX-015 |
| [`INF-003`](#INF-003) | Supabase · Prisma 연결 (Supavisor) 및 마이그레이션 승인 절차 | `Infra` | **6** | AGR-002 · DAT-001 · MCH-001 · REL-001 · REL-004 · TEC-001 |
| [`CTR-002`](#CTR-002) | Route Handler 8종 요청·응답 계약 및 에러 코드 체계 | `Contract` | **6** | ANA-002 · EVD-004 · MCK-001 · RNK-003 · RSV-003 · TST-004 |
| [`QRY-002`](#QRY-002) | AI SDK 단일 진입점 `lib/ai.ts` 및 Gemini 폴백 파서 | `Infra` | **4** | ANA-007 · EVD-001 · QRY-005 · SEC-002 |
| [`DAT-006`](#DAT-006) | 색인 파이프라인 및 `use cache` 계층 | `Write` | **3** | QRY-001 · QRY-007 · QRY-009 |
| [`ANA-002`](#ANA-002) | 이벤트 수집 (`sendBeacon` · `after()`) 및 지표 집계 Cron | `Write` | **3** | ANA-005 · ANA-007 · QRY-005 |
| [`EVD-001`](#EVD-001) | 근거 조립 · 4항목 검증 · 90일 경고 · 판정형 문구 필터 | `Read` | **3** | EVD-004 · EVD-005 · RNK-001 |

---

## 부록 B. 스프린트 배치

SRS §14.2의 스프린트 정의에 태스크를 배치한 것이다. **선행 태스크가 뒤 스프린트에 놓이는 역전은 생성 시 검증으로 차단된다.**

| 스프린트 | Part A | Part B |
| --- | --- | --- |
| **S-1 기반** | INF-001 · INF-002 · INF-003 · INF-008 · TEC-001 · TST-007 | UX-001 |
| **S0 계약·스키마** | CTR-001 · CTR-002 · CTR-005 · DAT-001 · DAT-008 · REL-004 · TST-008 | — |
| **S1 색인·계측** | DAT-006 · DAT-010 · MCK-001 · ANA-002 | UX-003 |
| **S2 필터·메뉴** | QRY-007 · QRY-009 | — |
| **S3 파싱·근거** | QRY-001 · QRY-002 · QRY-005 · EVD-001 · EVD-005 · SEC-002 · TST-001 | UX-004 |
| **S4 Top-3·관측** | EVD-004 · RNK-001 · RNK-003 · ANA-005 · REL-001 · TST-010 | UX-006 · UX-010 |
| **S5 예약 승계** | RSV-001 · ANA-007 · SEC-001 | UX-015 |
| **S6 결제** | RSV-003 · RSV-005 · TST-004 | — |
| **S7 가맹 콘솔** | MCH-001 · MCH-002 · MCH-003 · MCH-004 | UX-013 |
| **S8 대화방** | AGR-001 · AGR-002 · AGR-003 · AGR-005 · AGR-006 · TST-005 | UX-014 |

**Phase 경계** — S-1 ~ S4가 Phase 1 클로즈드 베타, S5 ~ S6이 Phase 1 말, S7 ~ S8이 Phase 2다 (SRS §10.4 게이트 조건과 정합).

---

## 부록 C. 요구사항 커버리지

`관련 SRS 섹션` 열에서 요구사항 ID를 추출해 자동 생성한 표다. **빈칸이 있으면 누락이다.**

| 요구사항 | 담당 태스크 | 건수 |
| --- | --- | --- |
| `REQ-FUNC-001` | DAT-001 · DAT-006 | 2 |
| `REQ-FUNC-002` | QRY-007 · UX-006 · UX-010 | 3 |
| `REQ-FUNC-003` | QRY-009 | 1 |
| `REQ-FUNC-004` | MCK-001 · QRY-001 · QRY-002 · UX-003 · UX-004 | 5 |
| `REQ-FUNC-005` | EVD-001 · EVD-004 · EVD-005 · UX-006 · UX-010 | 5 |
| `REQ-FUNC-006` | MCK-001 · RNK-001 · UX-006 | 3 |
| `REQ-FUNC-007` | DAT-001 · MCK-001 · RSV-001 · RSV-005 · UX-015 | 5 |
| `REQ-FUNC-008` | MCH-003 · MCH-004 · UX-013 | 3 |
| `REQ-FUNC-009` | AGR-001 · AGR-003 · AGR-006 · MCK-001 · UX-014 | 5 |
| `REQ-NF-001a` | REL-001 · RNK-003 · TST-010 | 3 |
| `REQ-NF-001b` | UX-003 | 1 |
| `REQ-NF-002` | DAT-006 | 1 |
| `REQ-NF-002b` | QRY-001 | 1 |
| `REQ-NF-004` | TST-010 · UX-003 | 2 |
| `REQ-NF-007` | RNK-003 · UX-004 | 2 |
| `REQ-NF-008` | DAT-010 | 1 |
| `REQ-NF-009` | REL-001 · REL-004 | 2 |
| `REQ-NF-010` | SEC-001 · SEC-002 | 2 |
| `REQ-NF-011` | RSV-003 · TST-004 · TST-008 | 3 |
| `REQ-NF-012` | DAT-008 · MCH-001 · TST-008 | 3 |
| `REQ-NF-013` | ANA-007 | 1 |
| `REQ-NF-014` | ANA-007 | 1 |
| `REQ-NF-015` | ANA-005 | 1 |
| `REQ-TEC-001` | TEC-001 · TST-007 | 2 |
| `REQ-TEC-002` | TEC-001 | 1 |
| `REQ-TEC-004` | INF-003 | 1 |
| `REQ-TEC-005` | INF-003 | 1 |
| `REQ-TEC-006` | INF-003 | 1 |
| `REQ-TEC-007` | INF-002 · UX-001 | 2 |
| `REQ-TEC-008` | QRY-002 | 1 |
| `REQ-TEC-010` | CTR-001 | 1 |
| `REQ-TEC-012` | TEC-001 · TST-008 | 2 |
| `REQ-TEC-013` | INF-001 | 1 |

자동 추출된 요구사항 **33종**이 담당 태스크를 가진다. 요구사항 ID가 `관련 SRS 섹션` 에 직접 표기되지 않은 태스크(인프라·계약·Mock·테스트 등)는 SRS 절 번호로 근거를 지목한다.

---

## 부록 D. 태스크로 만들지 않은 것

SRS에 언급되지만 **의도적으로 태스크에서 제외**한 항목이다. 임의 추가를 막는 것만큼 임의 누락을 밝히는 것도 필요하다.

| 항목 | 근거 | 사유 |
| --- | --- | --- |
| 다지점 공정 지점 산출 | §14.3 · §7 | v0.2+ 연기 대상 |
| 리뷰 3축 재가공 | §14.3 · §7.2 | v0.2+ 연기 대상 |
| AI 예약 에이전트 | §14.3 | v0.2+ 연기 대상 |
| 성분·접근성 데이터 커버리지 | §14.3 · §4.1 REQ-FUNC-010 | v0.1은 **스키마 필드만** — DAT-002에 포함되고 값 적재는 범위 밖 |
| 광고 상품 | §14.3 · ADR-004 | 도입 계획 없음 |
| 결제·정산 자체 구축 | §14.3 · LIM-01 | PG 위탁 |
| 지도·경로 API 연동 | §3.2 · LIM-06 | v0.1 미사용 |
| 실시간 매장 상태 연동 | §3.2 · §7.4 · LIM-07 | 제휴 검토 단계 — 단가 조건 미확정 |
| 마이크로프런트엔드 분리 | §7.3 | 단일 앱의 한계가 드러난 이후 검토 |
| 플랫폼 장애 대응 · 3,000 RPS 달성 | §15.1 | **미해소 항목** — 발주 측 결정 대기 중이라 태스크로 확정할 수 없음 |

---

**TASK-AIPLACE-MVP-001 · v3.0 · 2026-08-25 · Owner 5팀 · 태스크 56건**
