# -*- coding: utf-8 -*-
"""태스크 리스트 단일 원천 데이터 (TASK-AIPLACE-MVP-001).

이 파일이 태스크의 유일한 정의처다. `Blocks`(후행)는 `deps`에서 자동 역산되므로
직접 적지 않는다. 문서는 `tools/gen_task_list.py` 로 생성한다.

필드: (id, feature, srs, deps, complexity, type, sprint)
  type = Contract | Data | Read | Write | Test | Infra | NFR | Design
"""

EPIC_NAME = {
    "INF": "Platform & Infra",
    "TEC": "Constraint Gate",
    "CTR": "Contract",
    "DAT": "Data & Indexing",
    "MCK": "Mock",
    "QRY": "Query & Parsing",
    "EVD": "Evidence",
    "RNK": "Ranking",
    "RSV": "Reservation & Payment",
    "MCH": "Merchant Console",
    "AGR": "Agent Room",
    "ANA": "Analytics",
    "SEC": "Security & Privacy",
    "REL": "Reliability & Ops",
    "TST": "Test",
    "UX":  "UI/UX Design",
}

# Part A 표에서의 Epic 출력 순서
PART_A_ORDER = ["INF", "TEC", "CTR", "DAT", "MCK", "QRY", "EVD", "RNK",
                "RSV", "MCH", "AGR", "ANA", "SEC", "REL", "TST"]
PART_B_ORDER = ["UX"]

# Epic 앞에 붙는 안내 문단 (없으면 생략)
EPIC_NOTE = {
    "TEC": "> 제약은 선언이고, 이 Epic은 **선언을 어겼을 때 빌드가 실패하게 만드는 장치**다. "
           "S-1에서 먼저 작동시켜야 이후 스프린트의 위반이 즉시 드러난다(SRS §14.2).",
    "CTR": "> **Step 1 계약 태스크.** 백엔드와 프론트엔드가 공유하는 기준점이다. 계약이 기능 태스크 "
           "안에 묻혀 있으면 두 태스크가 같은 계약을 다르게 구현해도 탐지되지 않는다.",
    "MCK": "> **Step 1 Mock 태스크.** UI 작업이 백엔드 완성을 기다리지 않게 한다. SRS의 "
           "'빈 화면 금지'·'근거 없는 후보 반환 금지'가 요구하는 **실패·경계 상태**는 픽스처가 있어야 만들 수 있다.",
    "QRY": "> **2단 파싱이 이 Epic의 핵심**이다(ADR-T02). 결정론 파서가 질의의 70% 이상을 흡수하지 "
           "못하면 응답 시간(REQ-NF-001a)과 추론 비용(REQ-NF-013)이 동시에 무너진다.",
    "RSV": "> SRS §14.1에 따라 **REQ-FUNC-007은 REQ-FUNC-006과 DEP-01(PG 계약)에 선행 종속**하며, "
           "가맹 콘솔·대화방보다 **먼저** 착수한다.",
    "AGR": "> 대화방은 **서버 프로세스 없이** 구현한다 — DB 상태 + Realtime + lazy close(ADR-T06). "
           "마감 정확도가 Cron 주기에 종속되지 않아야 한다(SRS §9.3).",
    "TST": "> **Step 3 테스트 태스크.** SRS §9의 인수 기준(AC)을 실행 가능한 테스트 코드 작성 태스크로 "
           "변환한 것이다. 여기서 정리된 GWT가 각 Feature 태스크의 DoD 체크리스트로 삽입된다.",
    "UX":  "> C-TEC-004에 따라 **shadcn/ui에 존재하는 컴포넌트를 자체 구현하지 않는다**(D-08 · REQ-TEC-007). "
           "따라서 디자인 태스크는 컴포넌트 제작이 아니라 **토큰 정의 · 조합 규칙 · 화면 정의**가 중심이다.",
}

# (id, feature, srs, deps, complexity, type, sprint)
TASKS = [
    # ── INF · Platform & Infra ───────────────────────────────────────────
    ("INF-001", "Next.js App Router 프로젝트 초기화", "§1.5 C-TEC-001 · §14.1 디렉터리 구조", [], "M", "Infra", "S-1"),
    ("INF-002", "Tailwind CSS + shadcn/ui 설치 및 설정", "§1.5 C-TEC-004 · §4.3 REQ-TEC-007", ["INF-001", "UX-001"], "L", "Infra", "S-1"),
    ("INF-003", "로컬 Supabase 환경 구성 (`supabase start`)", "§1.5 C-TEC-003 · §4.3 REQ-TEC-006", [], "M", "Infra", "S-1"),
    ("INF-004", "Prisma 초기화 및 싱글턴 클라이언트 (`lib/db.ts`)", "§6.4 · §4.3 REQ-TEC-004", ["INF-001", "INF-003"], "M", "Infra", "S-1"),
    ("INF-005", "Supavisor 커넥션 구성 (`DATABASE_URL` / `DIRECT_URL`)", "§6.4 · §4.3 REQ-TEC-005 · ADR-T04", ["INF-004"], "M", "Infra", "S-1"),
    ("INF-006", "Vercel 프로젝트 연결 및 Git Push 배포 경로 확립", "§1.5 C-TEC-007 · §14.4", ["INF-001"], "L", "Infra", "S-1"),
    ("INF-007", "환경 변수 등록 및 필수값 검증", "§6.5 환경 변수", ["INF-006"], "L", "Infra", "S-1"),
    ("INF-008", "`proxy.ts` 요청 태깅 및 인증 훅", "§3.1 배포 토폴로지 · §3.3", ["INF-001"], "M", "Infra", "S-1"),
    ("INF-009", "`vercel.ts` Cron 스케줄 정의 (5종)", "§6.1 Cron 스케줄 · §4.3 REQ-TEC-013", ["INF-006"], "L", "Infra", "S-1"),
    ("INF-010", "마이그레이션 수동 승인 절차 수립", "§6.4 · §14.4 배포 파이프라인", ["INF-005"], "L", "Infra", "S-1"),
    ("INF-011", "네이버 지도 탭 임베드 진입 경로 구성", "§3.2 인터페이스 목록 · ADR-005", ["INF-006"], "M", "Infra", "S-1"),

    # ── TEC · Constraint Gate ────────────────────────────────────────────
    ("TEC-001", "모듈 디렉터리 스캐폴딩", "§3.3 모듈 구조 · §14.1", ["INF-001"], "M", "Infra", "S-1"),
    ("TEC-002", "ESLint `no-restricted-imports` 모듈 경계 규칙", "§4.3 REQ-TEC-002 · ADR-T01", ["CTR-006"], "M", "Infra", "S-1"),
    ("TEC-003", "`verify-constraints.mjs` 제약 검사 스크립트", "§4.3 REQ-TEC-001 · 003 · 004 · 005 · 008 · 011 · 015", ["TEC-001", "INF-005"], "H", "Infra", "S-1"),
    ("TEC-004", "빌드 명령에 품질 게이트 편입", "§4.3 REQ-TEC-012 · §14.4 · ADR-T08", ["TEC-002", "TEC-003", "INF-006"], "M", "Infra", "S-1"),
    ("TEC-005", "이벤트 스키마 계약 검사", "§4.3 REQ-TEC-012 · §10.2", ["TEC-004", "CTR-005"], "M", "Test", "S0"),

    # ── CTR · Contract (신설 · Step 1) ───────────────────────────────────
    ("CTR-001", "Server Action 9종 입출력 계약 (Zod DTO)", "§6.1 Server Actions", ["DAT-001", "DAT-003"], "H", "Contract", "S0"),
    ("CTR-002", "Route Handler 8종 요청·응답 계약", "§6.1 Route Handlers", ["CTR-001"], "M", "Contract", "S0"),
    ("CTR-003", "`ConditionSet` 스키마 (LLM 구조화 출력 계약)", "§6.6 AI 호출 규약 · §4.3 REQ-TEC-010", ["DAT-002"], "M", "Contract", "S0"),
    ("CTR-004", "에러 코드 체계 및 폴백 신호 규약", "§6.1 · §6.3-6 빈 화면 금지", ["CTR-001", "CTR-002"], "M", "Contract", "S0"),
    ("CTR-005", "계측 이벤트 계약 20종 (필수 속성 포함)", "§10.2 계측 구현", ["DAT-004"], "H", "Contract", "S0"),
    ("CTR-006", "모듈 공개 표면 계약 (`index.ts` 노출 규약)", "§3.3 모듈 구조 · §4.3 REQ-TEC-002", ["TEC-001"], "M", "Contract", "S-1"),

    # ── DAT · Data & Indexing ────────────────────────────────────────────
    ("DAT-001", "Prisma 스키마 — `Place` · `Dish` · `PriceProfile`", "§6.2 · §4.1 REQ-FUNC-001", ["INF-004"], "H", "Data", "S0"),
    ("DAT-002", "Prisma 스키마 — `Attribute` · `Verification` (성분·접근성 필드 포함)", "§6.2 · §4.1 REQ-FUNC-001 · 010", ["DAT-001"], "M", "Data", "S0"),
    ("DAT-003", "Prisma 스키마 — `AgentRoom` · `Proposal` · `Reservation` · `Payment`", "§6.2 · §4.1 REQ-FUNC-007 · 009", ["DAT-001"], "M", "Data", "S0"),
    ("DAT-004", "Prisma 스키마 — `Event` 및 일 단위 파티셔닝 원시 SQL 마이그레이션", "§6.2 · §10.2 계측 구현", ["DAT-001"], "M", "Data", "S0"),
    ("DAT-005", "`canonicalKey` 메뉴명 정규화 사전 및 정규화기", "§6.2 · §4.1 REQ-FUNC-001 · 003", ["DAT-001"], "H", "Data", "S0"),
    ("DAT-006", "색인 파이프라인 (dish + attribute 색인 적재)", "§4.1 REQ-FUNC-001 · ADR-001", ["DAT-002", "DAT-005"], "H", "Write", "S1"),
    ("DAT-007", "`use cache` 캐시 계층 및 태그 무효화", "§4.2 REQ-NF-002 · ADR-T05", ["DAT-006"], "M", "Read", "S1"),
    ("DAT-008", "RLS 정책 작성 (전 테이블)", "§6.4 · §4.2 REQ-NF-012", ["DAT-002", "DAT-003"], "H", "NFR", "S0"),
    ("DAT-009", "`audit_logs` 테이블 및 PostgreSQL 트리거", "§6.4 · §4.2 REQ-NF-012", ["DAT-008"], "M", "NFR", "S0"),
    ("DAT-010", "신선도 스캔 Cron (`/api/cron/freshness`)", "§6.1 · §4.2 REQ-NF-008", ["DAT-002", "INF-009"], "M", "Write", "S1"),
    ("DAT-011", "재확인 큐 적재 및 우선순위 상향 로직", "§6.1 · §4.2 REQ-NF-008", ["DAT-010"], "M", "Write", "S1"),

    # ── MCK · Mock (신설 · Step 1) ───────────────────────────────────────
    ("MCK-001", "Top-3 응답 픽스처 (정상 3건 / 근거 누락 / 후보 2건 이하)", "§6.3-2 · §4.1 REQ-FUNC-006", ["CTR-001"], "M", "Data", "S1"),
    ("MCK-002", "파싱 결과 픽스처 (캐시 히트 / 결정론 / LLM / 파싱 실패)", "§4.2.1 · §4.1 REQ-FUNC-004", ["CTR-003"], "M", "Data", "S1"),
    ("MCK-003", "대화방·제안 픽스처 (제안 0건 / 1건 / 5건 / 마감 경과)", "§9.3 · §4.1 REQ-FUNC-009", ["CTR-001"], "M", "Data", "S1"),
    ("MCK-004", "결제·웹훅 픽스처 (승인 / 거절 / 중복 수신 / 환불)", "§9.2 · §4.1 REQ-FUNC-007", ["CTR-002"], "M", "Data", "S1"),
    ("MCK-005", "Mock 모드 스위치 (환경 변수 · 로컬·프리뷰 한정)", "§6.5 환경 변수", ["INF-007"], "L", "Infra", "S1"),

    # ── QRY · Query & Parsing ────────────────────────────────────────────
    ("QRY-001", "결정론 파서 및 조건 카테고리 사전", "§4.2.1 · §4.1 REQ-FUNC-004 · ADR-T02", ["DAT-006", "CTR-003"], "H", "Read", "S3"),
    ("QRY-002", "AI SDK 단일 진입점 `lib/ai.ts` (타임아웃·재시도·토큰 상한)", "§6.6 · §4.3 REQ-TEC-008 · 009 · 010 · ADR-T10", ["INF-007"], "H", "Infra", "S3"),
    ("QRY-003", "Gemini 폴백 파서 (CTR-003 스키마 적용)", "§6.6 · §4.1 REQ-FUNC-004 · §1.5 C-TEC-005 · 006", ["QRY-002", "CTR-003"], "H", "Read", "S3"),
    ("QRY-004", "파싱 캐시 (정규화 질의 → ConditionSet)", "§4.2 REQ-NF-002b · §4.2.1", ["QRY-001", "DAT-007"], "M", "Read", "S3"),
    ("QRY-005", "`submitQuery` Server Action (2단 파싱 오케스트레이션)", "§6.1 Server Actions · §9.1", ["QRY-001", "QRY-003", "QRY-004", "CTR-001"], "M", "Write", "S3"),
    ("QRY-006", "폴백 가드 및 구조화 필터 전환", "§4.2 REQ-NF-007 · §6.3-6", ["QRY-005", "CTR-004", "UX-004"], "M", "Read", "S3"),
    ("QRY-007", "인당 가격대 필터 및 예상가 범위 추정", "§4.1 REQ-FUNC-002", ["DAT-006"], "M", "Read", "S2"),
    ("QRY-008", "`submitPriceFeedback` Server Action (편차 기록)", "§6.1 · §4.1 REQ-FUNC-002", ["QRY-007", "CTR-001"], "L", "Write", "S2"),
    ("QRY-009", "메뉴명 단독 질의 해석 (`canonicalKey` 조회)", "§4.1 REQ-FUNC-003", ["DAT-005", "DAT-006"], "M", "Read", "S2"),
    ("QRY-010", "유사 메뉴 대체 및 반경 확대 폴백", "§4.1 REQ-FUNC-003 · §6.3-6", ["QRY-009"], "M", "Read", "S2"),
    ("QRY-011", "`parse_path` 경로 태깅 계측", "§9.1 계측 필수 사항 · §10.1", ["QRY-005", "ANA-003"], "M", "Infra", "S3"),

    # ── EVD · Evidence ───────────────────────────────────────────────────
    ("EVD-001", "근거 문장 조립기 (선정 이유 + 근거 속성)", "§4.1 REQ-FUNC-005 · ADR-002", ["DAT-002"], "H", "Read", "S3"),
    ("EVD-002", "근거 4항목 검증기 및 90일 경과 경고", "§4.1 REQ-FUNC-005 · §6.3-2 · 5", ["EVD-001"], "M", "Read", "S3"),
    ("EVD-003", "판정형 문구 금지 필터", "§6.3-4 · §6.6 프롬프트 규약", ["EVD-001", "QRY-002"], "M", "Read", "S3"),
    ("EVD-004", "공유 카드 OG 이미지 Route Handler (`next/og`)", "§6.1 · §4.1 REQ-FUNC-005", ["EVD-002", "CTR-002", "UX-010"], "M", "Read", "S4"),
    ("EVD-005", "`reportMismatch` Server Action (재확인 큐 연동)", "§6.1 · §4.1 REQ-FUNC-005", ["EVD-002", "DAT-011", "CTR-001"], "M", "Write", "S3"),

    # ── RNK · Ranking ────────────────────────────────────────────────────
    ("RNK-001", "근거 미충족 후보 배제 및 Top-3 고정 선정", "§4.1 REQ-FUNC-006 · §6.3-2 · 3 · ADR-003", ["EVD-002", "QRY-007", "QRY-010"], "H", "Read", "S4"),
    ("RNK-002", "비교 축 생성", "§4.1 REQ-FUNC-006", ["RNK-001"], "M", "Read", "S4"),
    ("RNK-003", "결과 RSC 페이지 스트리밍 조립 (Suspense)", "§9.1 · §4.2 REQ-NF-001a · 001b", ["RNK-002", "QRY-005", "UX-005", "UX-006"], "H", "Read", "S4"),

    # ── RSV · Reservation & Payment ──────────────────────────────────────
    ("RSV-001", "`selectProposal` 선택 대상 조건 승계 Server Action", "§6.1 · §4.1 REQ-FUNC-007", ["RNK-003", "DAT-003", "CTR-001"], "M", "Write", "S5"),
    ("RSV-002", "주문량 기반 금액 산출기", "§4.1 REQ-FUNC-007", ["RSV-001"], "M", "Write", "S5"),
    ("RSV-003", "`requestPayment` Server Action 및 PG 클라이언트", "§6.1 · §4.2 REQ-NF-011 · DEP-T4", ["RSV-002", "INF-007", "UX-015"], "H", "Write", "S6"),
    ("RSV-004", "PG 웹훅 Route Handler (서명 검증 + 멱등 키)", "§6.1 · §9.2 · §4.2 REQ-NF-011 · §15-9", ["RSV-003", "DAT-003", "CTR-002"], "H", "Write", "S6"),
    ("RSV-005", "`cancelReservation` 및 전액 환불 처리", "§6.1 · §4.1 REQ-FUNC-007", ["RSV-004"], "M", "Write", "S6"),
    ("RSV-006", "노쇼 판정 Cron (`/api/cron/noshow`) 및 정산", "§6.1 · §4.1 REQ-FUNC-007", ["RSV-004", "INF-009"], "M", "Write", "S6"),

    # ── MCH · Merchant Console ───────────────────────────────────────────
    ("MCH-001", "Supabase Auth 연동 및 MFA 적용", "§4.2 REQ-NF-012 · §3.2", ["INF-003", "DAT-008"], "H", "Infra", "S7"),
    ("MCH-002", "`(merchant)` 라우트 그룹 및 전용 레이아웃 분리", "§14.1 · §8 사용자 특성", ["INF-002", "MCH-001", "UX-013"], "M", "Infra", "S7"),
    ("MCH-003", "매장 프로필 · 수용 조건 스키마", "§6.2 · §4.1 REQ-FUNC-008", ["DAT-002", "RSV-006"], "M", "Data", "S7"),
    ("MCH-004", "`saveMerchantProfile` Server Action", "§6.1 · §4.1 REQ-FUNC-008", ["MCH-003", "MCH-002", "CTR-001"], "M", "Write", "S7"),
    ("MCH-005", "EvidenceGuard — 근거 없는 문구 저장 차단", "§4.1 REQ-FUNC-008 · §6.3-2", ["MCH-004", "DAT-002"], "M", "Write", "S7"),
    ("MCH-006", "수용 조건 매칭기 (부적합 소환 차단)", "§4.1 REQ-FUNC-008", ["MCH-003"], "M", "Read", "S7"),

    # ── AGR · Agent Room ─────────────────────────────────────────────────
    ("AGR-001", "`createAgentRoom` Server Action 및 에이전트 3–5곳 소환", "§6.1 · §4.1 REQ-FUNC-009 · §9.3", ["MCH-006", "DAT-003", "CTR-001"], "H", "Write", "S8"),
    ("AGR-002", "Supabase Realtime 클라이언트 및 대화방 채널 구독", "§3.2 · §9.3 · ADR-T06", ["INF-003", "DAT-003"], "H", "Infra", "S8"),
    ("AGR-003", "`submitProposal` Server Action", "§6.1 · §4.1 REQ-FUNC-009", ["AGR-001", "MCH-005"], "M", "Write", "S8"),
    ("AGR-004", "조건 적합도 정렬 (가격 협상 필드 부재)", "§4.1 REQ-FUNC-009 · §6.3-7", ["AGR-003", "UX-014"], "M", "Read", "S8"),
    ("AGR-005", "마감 판정 — lazy close + 보조 Cron (`/api/cron/close-rooms`)", "§9.3 · §6.1 · §15-6", ["AGR-001", "AGR-002", "INF-009"], "H", "Write", "S8"),
    ("AGR-006", "유효 제안 0건 시 제안 없는 Top-3 복귀", "§6.3-6 · §4.1 REQ-FUNC-009", ["AGR-005", "RNK-003"], "M", "Read", "S8"),
    ("AGR-007", "불이행 신고 및 소환 가중치 하향", "§6.3-10", ["AGR-004"], "M", "Write", "S8"),

    # ── ANA · Analytics ──────────────────────────────────────────────────
    ("ANA-002", "`/api/events` Route Handler 및 `sendBeacon` 배치 수집", "§6.1 · §10.2", ["CTR-005", "CTR-002"], "M", "Write", "S1"),
    ("ANA-003", "`after()` 기반 서버 이벤트 적재", "§10.2 · ADR-T07", ["CTR-005"], "M", "Write", "S1"),
    ("ANA-004", "지표 집계 Cron (`/api/cron/aggregate`) 및 지표 마트", "§6.1 · §10.1 성과 지표", ["ANA-002", "ANA-003", "INF-009"], "H", "Write", "S1"),
    ("ANA-005", "계측 품질 점검 (누락률·결측률·스티칭·재현성)", "§10.2 · §10.3", ["ANA-004"], "M", "NFR", "S4"),
    ("ANA-006", "임계 알림 디스패처 (Slack · PagerDuty)", "§10.3 · §4.2 REQ-NF-015", ["ANA-005"], "M", "NFR", "S4"),
    ("ANA-007", "AI 추론 비용 집계 및 LLM 호출 비율 감시", "§4.2 REQ-NF-013 · §10.3", ["QRY-002", "ANA-004"], "M", "NFR", "S3"),
    ("ANA-008", "단위 경제 월간 리포트", "§4.2 REQ-NF-014 · §10.1", ["ANA-004"], "L", "Read", "S5"),

    # ── SEC · Security & Privacy ─────────────────────────────────────────
    ("SEC-001", "개인정보 30일 파기 Cron (`/api/cron/purge`)", "§6.1 · §4.2 REQ-NF-010", ["DAT-004", "INF-009"], "M", "NFR", "S5"),
    ("SEC-002", "프롬프트 개인정보 배제 검증", "§6.6 · §4.2 REQ-NF-010", ["QRY-002"], "M", "NFR", "S3"),
    ("SEC-003", "결제 스키마 카드 정보 컬럼 부재 검사", "§4.2 REQ-NF-011 · §6.2", ["DAT-003", "TEC-003"], "L", "Test", "S0"),

    # ── REL · Reliability & Ops ──────────────────────────────────────────
    ("REL-001", "Vercel Observability 연동 및 경로별 p95 관측", "§10.3 · §4.2 REQ-NF-001a · 001b", ["INF-006", "QRY-011"], "M", "NFR", "S4"),
    ("REL-002", "Cron 실행 실패 알림 (마지막 실행 시각 추적)", "§10.3 · §11.2 R-T3", ["INF-009", "ANA-006"], "M", "NFR", "S4"),
    ("REL-003", "Supavisor 풀 사용률 감시", "§10.3 · §11.2 R-T2", ["INF-005", "ANA-006"], "M", "NFR", "S4"),
    ("REL-004", "Supabase PITR 활성화 (RPO ≤ 5분)", "§6.4 · §4.2 REQ-NF-009", ["INF-003"], "L", "NFR", "S0"),
    ("REL-005", "Vercel 즉시 롤백 절차 문서화 및 훈련", "§11.2 R-T4 · §4.2 REQ-NF-009", ["INF-006"], "L", "NFR", "S4"),

    # ── TST · Test (신설 · Step 3) ───────────────────────────────────────
    ("TST-001", "US-1 예산·조건 동시 필터 GWT 테스트 (AC 6건 · 실패 2건 포함)", "§9.1 US-1 · 중립판 §9.1", ["CTR-001", "MCK-001", "MCK-002"], "M", "Test", "S3"),
    ("TST-002", "US-2 메뉴명 단독 질의 GWT 테스트 (AC 4건 · 실패 2건 포함)", "§9.2 · 중립판 §9.2", ["CTR-001", "MCK-001"], "M", "Test", "S2"),
    ("TST-003", "US-3 근거·확인 일자 GWT 테스트 (AC 4건 · 실패 2건 포함)", "중립판 §9.3", ["CTR-001", "MCK-001"], "M", "Test", "S3"),
    ("TST-004", "US-4 제안 승계·결제 GWT 테스트 (AC 4건 · 실패 2건 포함)", "§9.2 · 중립판 §9.4", ["CTR-002", "MCK-004"], "M", "Test", "S6"),
    ("TST-005", "US-5 매장 프로필 GWT 테스트 (AC 4건 · 실패 2건 포함)", "중립판 §9.5", ["CTR-001", "MCK-003"], "M", "Test", "S7"),
    ("TST-006", "US-6 소환·제안 비교 GWT 테스트 (AC 5건 · 실패 2건 포함)", "§9.3 · 중립판 §9.6", ["CTR-001", "MCK-003"], "M", "Test", "S8"),
    ("TST-007", "제약 게이트 위반 검증 (의도적 위반 → 빌드 실패 확인)", "§4.3 REQ-TEC-001 ~ 015 · §14.4", ["TEC-004"], "M", "Test", "S-1"),
    ("TST-008", "RLS 정책 접근 제어 테스트", "§6.4 · §4.2 REQ-NF-012", ["DAT-008"], "M", "Test", "S0"),
    ("TST-009", "PG 웹훅 멱등성 테스트 (중복 수신 시 상태 불변)", "§9.2 · §4.2 REQ-NF-011", ["CTR-002", "MCK-004"], "M", "Test", "S6"),
    ("TST-010", "부하 테스트 스크립트 (300 RPS · 경로별 p95 분리 측정)", "§4.2 REQ-NF-001a · 001b · 003 · §10.4 게이트 2", ["RNK-003"], "H", "Test", "S4"),
    ("TST-011", "초기 렌더 LCP 측정 (4G 조건)", "§4.2 REQ-NF-004", ["RNK-003", "UX-016"], "M", "Test", "S4"),

    # ── UX · UI/UX Design (Part B) ───────────────────────────────────────
    ("UX-001", "디자인 토큰 및 Tailwind 테마 정의", "§1.5 C-TEC-004", [], "M", "Design", "S-1"),
    ("UX-002", "shadcn/ui 컴포넌트 인벤토리 확정 (자체 제작 금지 목록)", "§4.3 REQ-TEC-007 · §1.5.1 D-08", ["UX-001"], "L", "Design", "S-1"),
    ("UX-003", "조건 입력 화면 (필수 입력 필드 0개)", "§9.2 · §4.1 REQ-FUNC-004", ["UX-002"], "M", "Design", "S0"),
    ("UX-004", "구조화 필터 폴백 화면 (해석 실패 표현 표기)", "§4.2.1 · §4.1 REQ-FUNC-004", ["UX-003"], "M", "Design", "S3"),
    ("UX-005", "로딩 스켈레톤 (500ms 내 렌더)", "§4.2 REQ-NF-001b", ["UX-003"], "M", "Design", "S1"),
    ("UX-006", "Top-3 후보 카드 (근거 4항목 표기)", "§4.1 REQ-FUNC-005 · 006 · §6.3-2", ["UX-002"], "H", "Design", "S2"),
    ("UX-007", "'확인 90일 경과' 경고 표시 규칙", "§6.3-5 · §4.1 REQ-FUNC-005", ["UX-006"], "L", "Design", "S3"),
    ("UX-008", "인당 예상가 범위 및 '가격 확인 필요' 표기", "§4.1 REQ-FUNC-002", ["UX-006"], "M", "Design", "S2"),
    ("UX-009", "비교 축 레이아웃", "§4.1 REQ-FUNC-006", ["UX-006"], "M", "Design", "S4"),
    ("UX-010", "공유 카드 비주얼 (OG 이미지 규격)", "§4.1 REQ-FUNC-005 · §6.1", ["UX-006"], "M", "Design", "S4"),
    ("UX-011", "빈 상태 · 오류 상태 정의 (빈 화면 금지)", "§6.3-6 · §4.2 REQ-NF-007", ["UX-004", "UX-005"], "M", "Design", "S3"),
    ("UX-012", "방문 후 결제액 입력 및 불일치 신고 폼", "§6.1 · §4.1 REQ-FUNC-002 · 005", ["UX-006"], "L", "Design", "S3"),
    ("UX-013", "가맹 콘솔 레이아웃 (설정 화면 ≤ 3개 · 필수 항목 ≤ 5개)", "§4.1 REQ-FUNC-008 · §8", ["UX-002"], "H", "Design", "S7"),
    ("UX-014", "대화방 카운트다운 및 제안 비교 화면", "§9.3 · §4.1 REQ-FUNC-009", ["UX-002"], "H", "Design", "S8"),
    ("UX-015", "예약 · 결제 화면 (재입력 필드 0개)", "§4.1 REQ-FUNC-007 · §9.2", ["UX-002"], "M", "Design", "S5"),
    ("UX-016", "모바일 초기 렌더 가이드 (LCP ≤ 2.5s)", "§4.2 REQ-NF-004", ["UX-001"], "M", "Design", "S1"),
]

SPRINT_ORDER = ["S-1", "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
SPRINT_TITLE = {
    "S-1": "S-1 기반", "S0": "S0 계약·스키마", "S1": "S1 색인·계측", "S2": "S2 필터·메뉴",
    "S3": "S3 파싱·근거", "S4": "S4 Top-3·관측", "S5": "S5 예약 승계", "S6": "S6 결제",
    "S7": "S7 가맹 콘솔", "S8": "S8 대화방",
}
