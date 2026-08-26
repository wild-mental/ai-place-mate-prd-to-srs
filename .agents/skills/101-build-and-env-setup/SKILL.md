---
name: 101-build-and-env-setup
description: AI-Place-Mate의 로컬 개발 환경 구성, 환경 변수, 빌드와 배포 절차. 처음 환경을 세우거나 환경 변수를 추가할 때, 빌드가 깨질 때 사용한다.
---

# 빌드 · 환경 구성

## 로컬 환경

```bash
pnpm install
npx supabase start                 # 로컬 Postgres · Studio 기동
npx prisma migrate dev             # DIRECT_URL 로 마이그레이션
pnpm dev                           # Next.js 개발 서버
```

로컬 DB는 **Supabase CLI로 띄운다** (C-TEC-003). 별도 Postgres를 설치하지 않는다 —
운영과 확장·정책이 갈라지면 로컬에서 통과한 것이 운영에서 깨진다.

## 환경 변수

`.env.example`을 원천으로 둔다. **변수를 추가하면 예시 파일에도 같이 추가한다.**
없는 변수 때문에 다른 사람의 로컬이 깨지는 게 가장 흔한 낭비다.

| 변수 | 용도 | 비고 |
| --- | --- | --- |
| `DATABASE_URL` | 애플리케이션 런타임 | Supavisor 풀러 `:6543` |
| `DIRECT_URL` | 마이그레이션 전용 | 직결 `:5432` |
| `NEXT_PUBLIC_SUPABASE_URL` | 클라이언트 Supabase | 공개돼도 되는 값 |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | 클라이언트 익명 키 | RLS가 보호한다 |
| `SUPABASE_SERVICE_ROLE_KEY` | 서버 전용 · RLS 우회 | **절대 클라이언트에 노출 금지** |
| `GOOGLE_GENERATIVE_AI_API_KEY` | Gemini API | 서버 전용 |
| `AI_MODEL_ID` | 모델 지정 | 코드에 상수로 두지 않는다 (D-07) |
| `CRON_SECRET` | Cron 엔드포인트 인증 | 공개 URL이므로 필수 |

**`NEXT_PUBLIC_` 접두는 브라우저에 그대로 나간다.** 비밀값에 붙이지 않는다.

배포 환경 변수는 Vercel 프로젝트 설정에 넣는다. Preview와 Production을 나눠 관리한다.

## 빌드

```bash
pnpm build          # next build — verify-constraints 가 여기서 돈다
pnpm typecheck
pnpm lint
pnpm test
```

## 품질 게이트

외부 CI를 두지 않는다 (D-06). 대신 **Vercel 빌드 단계가 게이트**다.

`scripts/verify-constraints.mjs`가 REQ-TEC 위반을 검사하고, 걸리면 빌드가 실패해
배포가 차단된다. 외부 CI에서 막는 것과 차단 효과는 같다 (ADR-T08).

게이트를 우회하려 하지 않는다. 게이트가 틀렸다면 게이트를 고친다.

## 배포

Git Push가 곧 배포다 (C-TEC-007).

```
push → Vercel 빌드 트리거 → verify-constraints → next build → 배포
```

- `main` 푸시 = Production
- 그 외 브랜치 = Preview 배포. PR에 URL이 자동으로 붙는다
- 배포 스크립트를 따로 만들지 않는다

## 현재 파일 구조 확인

```bash
tree -L 4 -a -I 'node_modules|.git|.next|__pycache__|.DS_Store'
```

## 빌드가 깨졌을 때

1. 스킬 `100-error-fixing-process`의 7단계를 따른다
2. `verify-constraints` 실패면 **제약 위반이다** — 스킬 `300-tech-constraints-guardrails` 확인
3. Prisma 관련이면 `DATABASE_URL` / `DIRECT_URL`을 바꿔 쓰지 않았는지 본다 (스킬 `302`)
