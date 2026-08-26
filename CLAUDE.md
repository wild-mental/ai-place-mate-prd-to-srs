# AI-Place-Mate

Claude Code가 세션 시작 시 자동으로 읽는 파일이다.
**여기는 짧게 유지한다.** 상세는 스킬로 빼서 필요할 때 꺼내 읽게 한다.

---

## 이 저장소의 상태

기획이 끝났고 **구현이 시작되지 않았다.** SRS·설계 문서·태스크 59건·실행 일정이 확정돼 있고,
GitHub Project #25가 이슈 단위로 돌고 있다.

**없는 기능을 만들지 않는다.** 할 일은 `docs/tasks/<TASK-ID>.md` 에 이미 적혀 있다.

## 무엇을 만드는가

모임 장소 선정을 자동화한다. 자연어 한 줄로 조건을 받아 후보를 추천하고 **근거를 함께 제시**한다.
상세는 `.agents/rules/001-project-overview.md`.

## 기술 스택 — 확정 사항

발주 측이 제약(C-TEC-001~007)으로 못박았다. **대안을 제안하기 전에 SRS §15 충돌 대장을 읽는다.**

- **Next.js App Router 단일 풀스택** — 프론트/백엔드를 분리하지 않는다
- **서버 로직은 Server Action · Route Handler · RSC 셋뿐**
- **Prisma + Supabase PostgreSQL** — 런타임은 풀러(`:6543`), 마이그레이션은 직결(`:5432`)
- **Tailwind + shadcn/ui**
- **Vercel AI SDK + Google Gemini** — 모델 ID는 환경 변수로만
- **Vercel 단일 배포** — Git Push가 곧 배포. 외부 CI 없음

도입하지 않는 것: 별도 백엔드 프로세스 · 내부 HTTP 호출 · 캐시 서버 · 메시지 큐 · 상시 스케줄러 · 외부 CI.
전체 표는 `.agents/rules/002-tech-stack.md`.

## 작업 순서

1. `docs/plan-docs/[TaskList]AI-Place-Mate-Task-List.md` — 태스크와 선행 관계
2. `docs/tasks/<TASK-ID>.md` — AC · DoD · **실패 시나리오**
3. 참조된 SRS 절과 설계 다이어그램
4. **선행이 안 끝났으면 시작하지 않는다**

절차 전체는 스킬 `400-task-execution-workflow`.

---

## 스킬 라우팅

프로젝트 고유 규범이다. 상황이 맞으면 자동으로 읽힌다.

| 스킬 | 언제 |
| --- | --- |
| `300-tech-constraints-guardrails` | 의존성 추가 · 인프라 도입 · 배포 설정 변경 — **제약 위반 차단** |
| `301-server-boundary-rules` | 서버 로직을 어디에 놓을지 · 캐시 · 비동기 · Cron |
| `302-data-access-rules` | 스키마 변경 · 쿼리 · RLS · 트랜잭션 |
| `303-ai-integration-rules` | AI 호출 · 프롬프트 · 2단 파싱 |
| `400-task-execution-workflow` | 태스크 시작·진행·완료 |
| `401-prototype-visual-rules` | **로컬 시각 프로토타입** 화면·상태·카드·카피 — 지어내기 차단 |
| `100-error-fixing-process` | 에러·빌드 실패 진단 |
| `101-build-and-env-setup` | 환경 구성 · 환경 변수 · 배포 |
| `200-git-commit-push-pr` | 커밋 · 브랜치 · PR |
| `201-code-commenting` | 주석 기준 |
| `202-github-issue-handling` | 이슈 · Project #25 조작 |

외부 스킬(마켓플레이스 설치)은 프레임워크 사용법을 담당한다 —
`vercel-react-best-practices` · `ai-sdk` · `shadcn` · `supabase` ·
`supabase-postgres-best-practices` · `prisma-client-api` · `prisma-database-setup` ·
`web-design-guidelines` · `tdd` · `webapp-testing`.

## 서브에이전트

| 에이전트 | 언제 |
| --- | --- |
| `nextjs-server` | Server Action · Route Handler · RSC · 캐시 |
| `prisma-data` | 스키마 · 마이그레이션 · 쿼리 · RLS |
| `ai-gemini` | AI SDK · Gemini · 2단 파싱 |
| `ui-shadcn` | 화면 · 컴포넌트 · 접근성 |

---

## 자주 걸리는 것

| 증상 | 원인 |
| --- | --- |
| 빌드가 `verify-constraints`에서 실패 | 제약 위반 — 우회하지 말고 스킬 `300` |
| 마이그레이션이 멈춤 / 커넥션 고갈 | `DATABASE_URL` ↔ `DIRECT_URL` 혼용 |
| 캐시가 무효화되지 않음 | `cacheTag` 누락 |
| Server Action에 GET 캐시가 안 먹음 | Server Action은 항상 POST다 |
| 프롬프트를 고쳤는데 옛 결과 | 파싱 캐시 미무효화 |

## 문서를 건드릴 때

- `docs/plan-docs/[TaskList]...` 와 `[Plan]...` 은 **생성물이다.** 직접 편집하지 않는다.
  `tools/tasks_data.py` 를 고치고 생성기를 다시 돌린다
- 문서를 옮기거나 이름을 바꿨으면 `python3 tools/verify_links.py`
- 하네스 구성은 `docs/ops-docs/[Ops]AI-Harness-Guide.md`
