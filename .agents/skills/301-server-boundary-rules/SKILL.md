---
name: 301-server-boundary-rules
description: Next.js App Router에서 서버 코드를 어디에 어떻게 쓸지 정한다. Server Action·Route Handler·RSC 선택, 모듈 경계, 캐시와 비동기 처리. 서버 로직을 추가하거나 옮길 때 사용한다.
---

# 서버 경계 규칙

## 진입점은 셋뿐이다

C-TEC-002가 정한다. 네 번째는 없다.

| 상황 | 선택 | 위치 |
| --- | --- | --- |
| 화면 렌더용 읽기 | RSC 직접 조회 | `app/**/page.tsx` |
| 사용자 변경 작업 | Server Action | `app/actions/*.ts` |
| 외부 시스템 수신 (웹훅·Cron) | Route Handler | `app/api/**/route.ts` |
| 캐시 가능한 GET | Route Handler | `app/api/**/route.ts` |

**Server Action은 항상 POST다.** GET 캐시가 필요하면 Route Handler를 쓴다.
이걸 헷갈리면 캐시가 안 먹는 이유를 한참 찾게 된다.

## 3계층 — 어디에 무엇을 두는가

Spring의 Controller/Service/Repository가 Next.js에서 어떻게 대응되는지다.
계층 이름을 옮겨오는 게 아니라 **책임의 경계**를 옮겨온다.

```
app/actions/*.ts        진입점 — 입력 검증, 인증 확인, 결과 형태 결정
   ↓ 함수 호출 (HTTP 아님 · D-02)
src/modules/<name>/index.ts   도메인 — 규칙과 조합. 이 파일이 모듈의 유일한 공개 표면
   ↓
src/lib/db.ts           데이터 — Prisma 접근
```

### 진입점 (Server Action · Route Handler)

- **입력을 신뢰하지 않는다.** Server Action 인자는 클라이언트가 보낸 값이다.
  스키마로 파싱한 뒤 도메인에 넘긴다
- 인증·권한을 여기서 확인한다
- 도메인 예외를 사용자가 볼 형태로 바꾼다. 스택 트레이스를 그대로 노출하지 않는다
- **비즈니스 규칙을 여기에 쓰지 않는다**

### 도메인 (`src/modules/<name>/`)

- `index.ts` 가 **유일한 공개 표면**이다 (REQ-TEC-002).
  다른 모듈의 내부 파일을 직접 import하지 않는다
- Next.js에 의존하지 않는다 — `next/headers`, `cookies()` 를 도메인에서 부르지 않는다.
  필요한 값은 인자로 받는다. 그래야 테스트가 된다
- 모듈 목록: `indexing · query · evidence · ranking · agentroom · merchant · reservation · analytics`

### 데이터 (`src/lib/db.ts`)

- Prisma 클라이언트는 싱글턴으로 둔다 (개발 중 HMR로 연결이 새는 것을 막는다)
- 트랜잭션은 도메인이 결정하고 여기서 실행한다

## 캐시

- 읽기 캐시는 `use cache` + `cacheTag`로 건다
- 무효화는 `updateTag`로 한다. 태그를 안 붙이면 무효화할 방법이 없다
- **캐시 서버를 도입하지 않는다** (D-03)
- 목표: `use cache` 히트율 ≥ 70% (REQ-NF-002)

## 비동기

- 응답 후 처리는 `after()` 를 쓴다 — 로그 적재, 집계, 알림
- 재시도가 필요하거나 유실되면 안 되는 작업은 **DB 큐 테이블**에 넣고 Cron이 처리한다
- **메시지 큐를 도입하지 않는다** (D-04)

## 주기 작업

- `app/api/cron/<name>/route.ts` 에 두고 `vercel.ts` 의 crons에 등록한다
- 현재 정의된 것: `freshness · close-rooms · aggregate · purge · noshow`
- **Cron 엔드포인트는 인증한다.** 공개 URL이므로 누구나 부를 수 있다

## 안티패턴

| ❌ | 왜 | ✅ |
| --- | --- | --- |
| Server Action에서 다른 Server Action을 `fetch`로 호출 | 내부 HTTP 홉 (D-02) | 도메인 함수를 직접 호출 |
| 도메인 모듈에서 `cookies()` 호출 | 테스트 불가 · 계층 침범 | 진입점이 값을 뽑아 인자로 전달 |
| `page.tsx`에 Prisma 쿼리 직접 작성 | 재사용·테스트 불가 | 모듈 `index.ts` 경유 |
| Server Action으로 캐시 가능한 GET 처리 | POST라 캐시 안 됨 | Route Handler |
| `use cache`에 태그 없이 캐싱 | 무효화 불가 | `cacheTag` 필수 |

## 원천

- SRS `§6.1 서버 진입점 목록` — 액션·핸들러 전체 명세
- SRS `§14.1 디렉터리 구조`
- 설계 문서 `§1.2 컴포넌트 다이어그램`
