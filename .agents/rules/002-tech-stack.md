---
description: AI-Place-Mate 기술 스택 — 제약 C-TEC-001~007이 확정한 구성
globs: ["**/*"]
alwaysApply: true
---
# Technical Stack

이 스택은 **선택지가 아니라 확정 사항**이다. 발주 측이 제약(C-TEC)으로 못박았고,
SRS `§1.5`가 원천이다. 대안을 제안하기 전에 §15 충돌 대장을 먼저 읽는다.

## 단일 풀스택 (C-TEC-001 · 002)

- **Framework:** Next.js App Router — 프론트엔드와 백엔드를 분리하지 않는다
- **서버 로직:** Server Actions (`app/actions/`) · Route Handlers (`app/api/`) · RSC 직접 조회
- **Language:** TypeScript
- **런타임:** Node.js (Edge 런타임은 Prisma 제약으로 기본 아님)

## 데이터 (C-TEC-003)

- **ORM:** Prisma
- **DB:** Supabase PostgreSQL — 로컬은 Supabase CLI, 배포는 Supabase 호스팅
- **연결:** 애플리케이션은 Supavisor 트랜잭션 풀러(`:6543`, `DATABASE_URL`),
  마이그레이션은 직결(`:5432`, `DIRECT_URL`)
- **권한:** Row Level Security. 정책은 `supabase/policies/`에 둔다

## UI (C-TEC-004)

- **Styling:** Tailwind CSS
- **Components:** shadcn/ui — `src/components/ui/`
- shadcn/ui에 있는 컴포넌트를 직접 다시 만들지 않는다 (D-08)

## AI (C-TEC-005 · 006)

- **SDK:** Vercel AI SDK — 자체 추론 서버를 두지 않는다
- **Provider:** Google Gemini (`@ai-sdk/google`)
- **모델 지정:** 환경 변수로만 한다. 코드에 모델 ID를 상수로 두지 않는다 (D-07)
- **구조화 출력:** `generateText({ model, output: Output.object({ schema }) })`

## 배포 (C-TEC-007)

- **Platform:** Vercel 단일화. Git Push가 곧 배포다
- **품질 게이트:** 외부 CI를 두지 않는다. `scripts/verify-constraints.mjs`가
  Vercel 빌드 단계에서 REQ-TEC 위반을 막는다 (D-06)
- **주기 작업:** Vercel Cron Jobs → `app/api/cron/*/route.ts` (D-05)

## 도입하지 않는 것

제약에서 파생된 금지 목록이다. 필요해 보여도 먼저 §15에 충돌로 기록한다.

| 금지 | 근거 | 대신 |
| --- | --- | --- |
| 별도 백엔드 프로세스 (Express·NestJS) | D-01 | Server Actions · Route Handlers |
| 서비스 간 내부 HTTP 호출 | D-02 | 모듈 함수 직접 호출 |
| 캐시 서버 (Redis·Memcached) | D-03 | Next.js `use cache` + PostgreSQL |
| 메시지 큐 (Kafka·SQS) | D-04 | `after()` + DB 큐 테이블 |
| 상시 스케줄러 (cron 데몬) | D-05 | Vercel Cron Jobs |
| 외부 CI (GitHub Actions) | D-06 | Vercel 빌드 게이트 |

## 디렉터리 구조

SRS `§14.1`이 원천이다. 새 파일을 놓을 자리가 애매하면 그 절을 먼저 본다.

```
app/          라우트 그룹 · actions/ (Server Actions) · api/ (Route Handlers)
src/modules/  도메인 모듈 — index.ts 가 유일한 공개 표면 (REQ-TEC-002)
src/lib/      db · ai · cache · realtime · observability
src/components/ui/  shadcn/ui
prisma/       schema.prisma · migrations/
supabase/     config.toml · policies/
scripts/verify-constraints.mjs   빌드 게이트
proxy.ts      인증 · 요청 태깅
```

## See also

- [003-development-guidelines.md](003-development-guidelines.md)
- `docs/tech-design-docs/[SRS]AI-Place-Mate-SRS-v1_0.md` §1.5 제약 · §6 서버 진입점 · §14 구현 계획
