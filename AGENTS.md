# AI-Place-Mate — Agent Instructions

여러 AI 코딩 도구(Claude Code · Cursor · Antigravity · Gemini CLI · Codex 등)가 공통으로 읽는
최상위 규칙 파일이다. 도구별 설정은 이 내용을 중복하지 않고 참조한다.

---

## 프로젝트

모임 장소 선정을 자동화하는 서비스다. 자연어 한 줄로 조건을 받아 후보를 추천하고
**근거를 함께 제시**한다. 추천만 하고 끝내지 않는 것이 이 제품의 차별점이다.

**이 저장소는 기획이 끝난 상태다.** SRS·설계 문서·태스크 59건·실행 일정이 확정돼 있다.
할 일은 `docs/tasks/<TASK-ID>.md` 에 이미 적혀 있다. **없는 기능을 만들지 않는다.**

## 기술 제약 (C-TEC-001~007)

발주 측이 확정한 제약이다. 기술적으로 더 나은 대안이 있어도 **조용히 우회하지 않는다.**
제약이 요구사항을 실제로 깨뜨리는 경우는 SRS §15 충돌 대장에 기록하고 사람에게 판단을 요청한다.

| ID | 제약 |
| --- | --- |
| C-TEC-001 | Next.js App Router 단일 풀스택. 프론트/백엔드를 분리하지 않는다 |
| C-TEC-002 | 서버 로직은 Server Actions 또는 Route Handlers. 별도 백엔드 서버 없음 |
| C-TEC-003 | Prisma + Supabase — 로컬은 Supabase CLI, 배포는 Supabase PostgreSQL |
| C-TEC-004 | Tailwind CSS + shadcn/ui |
| C-TEC-005 | AI는 Vercel AI SDK로 외부 API 호출. 자체 추론 서버 없음 |
| C-TEC-006 | Google Gemini 기본. 환경 변수만으로 모델 교체 가능해야 한다 |
| C-TEC-007 | Vercel 단일 배포. CI 설정 없이 Git Push로 자동 배포 |

### 도입하지 않는 것 (파생 규범 D-01~D-08)

| 금지 | 대신 |
| --- | --- |
| 별도 백엔드 프로세스 · 상시 워커 | Server Actions · Route Handlers |
| 모듈 간 내부 HTTP 호출 | 함수 직접 호출 |
| 캐시 서버 (Redis 등) | Next.js `use cache` + PostgreSQL |
| 메시지 큐 (Kafka 등) | `after()` + DB 큐 테이블 |
| 상시 스케줄러 (cron 데몬) | Vercel Cron Jobs → Route Handler |
| 외부 CI (GitHub Actions 등) | Vercel 빌드 게이트 (`scripts/verify-constraints.mjs`) |
| 코드에 모델 ID 상수 | 환경 변수 |
| shadcn/ui 컴포넌트 재구현 | `npx shadcn add` |

## 서버 코드 배치

C-TEC-002가 진입점을 셋으로 제한한다. **취향이 아니라 표로 결정한다.**

| 상황 | 선택 |
| --- | --- |
| 화면 렌더용 읽기 | RSC 직접 조회 |
| 사용자 변경 작업 | Server Action (`app/actions/`) |
| 외부 시스템 수신 (웹훅 · Cron) | Route Handler (`app/api/`) |
| 캐시 가능한 GET | Route Handler — Server Action은 항상 POST라 HTTP 캐시가 없다 |

**모듈 경계** — `src/modules/<name>/index.ts` 가 유일한 공개 표면이다 (REQ-TEC-002).

## 성능 기준

| 기준 | 값 |
| --- | --- |
| 결정론 경로 응답 | p95 ≤ 1,000ms |
| LLM 폴백 경로 응답 | p95 ≤ 2,500ms |
| `use cache` 히트율 | ≥ 70% |
| 파싱 캐시 히트율 | ≥ 60% |

자연어 파싱은 **결정론 파서가 먼저** 처리하고 실패분만 LLM이 받는다 (ADR-T02).
이 순서를 뒤집으면 응답 시간 기준이 깨지고 비용이 트래픽에 선형으로 붙는다.

## 코드 스타일

- 주석은 **WHY**를 쓴다. WHAT은 코드가 말한다. 쓸모없어진 주석은 즉시 지운다
- 주석·커밋 메시지는 한국어로 쓴다. 요구사항을 참조할 때는 ID를 적는다 (`REQ-NF-001a`, `D-07`)
- 사용자 입력은 스키마로 검증한 뒤 도메인에 들인다. Server Action 인자는 신뢰할 수 없다
- 비밀값은 서버에만 둔다. `NEXT_PUBLIC_` 접두는 공개해도 되는 값에만 쓴다

## Git

- 브랜치: `<type>/<issue-number>-<short-description>` — 이슈 번호를 반드시 넣는다
- 커밋: Conventional Commits · 원자적으로 · 각 커밋이 빌드되는 상태로
- `main` 직접 커밋 금지. PR은 draft로 먼저 열고 본문에 `Closes #<번호>`

## 완료 정의

- Acceptance Criteria 전항 충족 — **실패 시나리오 포함**
- 타입 검사 · 린트 · 테스트 통과
- `scripts/verify-constraints.mjs` 통과 (제약 위반 0건)
- 문서와 실제가 어긋났으면 문서를 고친다

## 원천 문서

| 문서 | 무엇 |
| --- | --- |
| `docs/tech-design-docs/[SRS]AI-Place-Mate-SRS-v1_0.md` | **권위 있는 요구사항** — 제약 반영판 |
| `docs/tech-design-docs/[Diagrams]AI-Place-Mate-Diagrams.md` | 설계 다이어그램 32개 |
| `docs/plan-docs/[TaskList]AI-Place-Mate-Task-List.md` | 태스크 59건 (생성물 — 직접 편집 금지) |
| `docs/tasks/<TASK-ID>.md` | 태스크별 AC · DoD · 실패 시나리오 |
| `.agents/rules/` | 상세 규칙 3종 |
| `.agents/skills/` | 상황별 스킬 (SSOT · 각 도구에 심볼릭 링크) |
