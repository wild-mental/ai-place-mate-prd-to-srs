---
name: 300-tech-constraints-guardrails
description: AI-Place-Mate의 기술 제약(C-TEC-001~007)과 파생 규범(D-01~D-08) 위반을 사전에 잡는다. 새 의존성 추가, 인프라 구성요소 도입, 서버 코드 배치, 배포 설정 변경 전에 반드시 확인한다.
---

# 기술 제약 가드레일

## 언제 쓰는가

- 새 npm 패키지를 추가하려 할 때
- "여기는 Redis를 쓰면 빠른데" 같은 판단이 들 때
- 서버 코드를 어디에 놓을지 정할 때
- 배포·스케줄링·CI 설정을 건드릴 때

## 왜 있는가

C-TEC-001~007은 발주 측이 확정한 제약이다. 기술적으로 더 나은 대안이 있어도
**제약을 조용히 우회하면 안 된다.** 우회는 발견이 늦고, 발견 시점에는 이미 되돌리기 비싸다.
제약이 요구사항을 깨뜨리는 경우는 실제로 존재하며, SRS §15 충돌 대장이 그것을 기록한다.
새 충돌을 찾으면 **거기에 적고 논의한다.** 코드로 몰래 해결하지 않는다.

## 체크리스트 — 새 의존성·구성요소

아래에 걸리면 멈춘다.

| 하려는 것 | 판정 | 근거 | 대신 |
| --- | --- | --- | --- |
| Express·NestJS·Fastify 서버 추가 | ❌ | D-01 | Server Actions · Route Handlers |
| 상시 구동 워커 프로세스 | ❌ | D-01 | `after()` · Vercel Cron |
| 내부 모듈을 HTTP로 호출 | ❌ | D-02 | `src/modules/<name>/index.ts` 함수 호출 |
| Redis·Memcached·Upstash 캐시 | ❌ | D-03 | `use cache` + `cacheTag` · PostgreSQL |
| Kafka·SQS·RabbitMQ | ❌ | D-04 | `after()` + DB 큐 테이블 |
| node-cron·agenda 등 스케줄러 | ❌ | D-05 | Vercel Cron → `app/api/cron/*/route.ts` |
| GitHub Actions·CircleCI 파이프라인 | ❌ | D-06 | `scripts/verify-constraints.mjs` (빌드 게이트) |
| 코드에 모델 ID 상수 (`"gemini-..."`) | ❌ | D-07 | 환경 변수로만 |
| shadcn/ui에 있는 컴포넌트 재구현 | ❌ | D-08 | `npx shadcn add <component>` |
| Prisma 아닌 쿼리 빌더 병행 | ⚠️ | C-TEC-003 | 원시 SQL이 필요하면 Prisma `$queryRaw` |
| Vercel 외 배포 타깃 추가 | ❌ | C-TEC-007 | — |

## 체크리스트 — 서버 코드 배치

```
화면에 보여줄 데이터를 읽는가?           → RSC에서 직접 조회
사용자가 무언가를 바꾸는가?              → app/actions/ 의 Server Action
외부(웹훅·Cron)가 HTTP로 들어오는가?     → app/api/ 의 Route Handler
GET인데 HTTP 캐시가 필요한가?            → Route Handler
                                          (Server Action은 항상 POST라 캐시 불가)
```

## 체크리스트 — AI 호출

- 결정론 파서를 **먼저** 태웠는가? 흡수율 ≥ 70%가 목표다 (ADR-T02)
- 파싱 캐시를 조회했는가? 히트율 ≥ 60%가 REQ-NF-002b다
- 모델 ID가 환경 변수에서 오는가? (D-07)
- 구조화 출력에 `generateText({ output: Output.object({ schema }) })`를 쓰는가?
- LLM 실패 시 사용자에게 보여줄 경로가 있는가? 폴백의 폴백이 없으면 장애가 그대로 노출된다

## 위반을 발견했을 때

1. **구현 전이면** — 위 표의 "대신"으로 바꾼다
2. **이미 들어갔으면** — 제거 비용을 재고 태스크로 만든다. 조용히 두지 않는다
3. **제약이 요구사항을 실제로 깨뜨리면** — SRS §15 충돌 대장에 항목을 추가하고
   사람에게 판단을 요청한다. 미해결 2건(플랫폼 가용성 SLA, 3,000 RPS)이 이미 그런 사례다

## 원천

- `docs/tech-design-docs/[SRS]AI-Place-Mate-SRS-v1_0.md` §1.5 제약 · §1.5.1 파생 규범 · §15 충돌 대장
- 빌드 게이트: `scripts/verify-constraints.mjs`
