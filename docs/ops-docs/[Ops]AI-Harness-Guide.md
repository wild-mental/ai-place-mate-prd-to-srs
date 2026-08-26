# AI 하네스 구성 가이드

이 저장소가 AI 코딩 에이전트에게 무엇을 어떻게 알려주는지 정리한 문서다.
구성은 [AI-multivender-harness-sample](https://github.com/wild-mental/AI-multivender-harness-sample)의
규약을 따르되, **이 프로젝트의 스택과 목표에 맞게 다시 썼다.**

---

## 1. 구조

```
AGENTS.md                도구 공통 최상위 규칙 (Claude Code · Cursor · Antigravity · Gemini CLI · Codex …)
CLAUDE.md                Claude Code 진입점 — 짧게 유지하고 스킬로 라우팅
.agents/
├── rules/               상세 규칙 3종 (항상 적용)
├── skills/              스킬 SSOT — 각 도구 디렉터리에 심볼릭 링크
└── workflows/           문서 생성 워크플로
.claude/
├── agents/              서브에이전트 4종
└── skills/ → ../.agents/skills   (심볼릭 링크)
```

**스킬을 `.agents/skills/`에 두는 이유**는 도구마다 복사본을 만들지 않기 위해서다.
`npx skills add`가 이 배치를 기본으로 쓰고, 설치 시 각 도구 디렉터리에 링크를 걸어준다.

## 2. 무엇을 어디에 쓰는가

| 성격 | 위치 | 이유 |
| --- | --- | --- |
| 항상 참이어야 하는 것 | `AGENTS.md` · `.agents/rules/` | 매 세션 주입된다 |
| 상황이 되면 꺼내 읽을 것 | `.agents/skills/*/SKILL.md` | 필요할 때만 컨텍스트를 쓴다 |
| 격리된 컨텍스트가 필요한 작업 | `.claude/agents/*.md` | 메인 대화를 오염시키지 않는다 |

`CLAUDE.md`는 **짧게 유지한다.** 매 대화에 주입되므로 여기가 길어지면 실제 작업에 쓸 컨텍스트가 준다.

## 3. 규칙 3종

| 파일 | 내용 |
| --- | --- |
| `001-project-overview.md` | 무엇을 왜 만드는가 · 대상 사용자 · 개발 철학 |
| `002-tech-stack.md` | C-TEC이 확정한 스택 · 도입하지 않는 것 · 디렉터리 구조 |
| `003-development-guidelines.md` | 작업 진입 절차 · 계층 규칙 · 성능 기준 · 완료 정의 |

## 4. 스킬 — 자체 작성 10종

프로젝트 고유 규범이다. **마켓플레이스 스킬이 모르는 것**만 담았다.

| 스킬 | 언제 |
| --- | --- |
| `100-error-fixing-process` | 에러·빌드 실패 7단계 진단 |
| `101-build-and-env-setup` | 환경 구성 · 환경 변수 · 배포 |
| `200-git-commit-push-pr` | 커밋 · 브랜치 · PR |
| `201-code-commenting` | 주석 기준 |
| `202-github-issue-handling` | 이슈 · Project #25 조작 |
| `300-tech-constraints-guardrails` | **제약 위반 차단** — 의존성·인프라·배포 변경 전 |
| `301-server-boundary-rules` | 서버 코드 배치 · 캐시 · 비동기 · Cron |
| `302-data-access-rules` | Prisma 연결 · 마이그레이션 · RLS · 트랜잭션 |
| `303-ai-integration-rules` | AI SDK · Gemini · 2단 파싱 |
| `400-task-execution-workflow` | 태스크 시작·진행·완료 |

## 5. 스킬 — 마켓플레이스 설치 10종

프레임워크 사용법은 공개 스킬에 맡긴다. 우리가 다시 쓸 이유가 없다.
[skills.sh](https://www.skills.sh/)에서 **스택 적합성과 실사용량**을 기준으로 골랐다.

| 스킬 | 패키지 | 채택 근거 |
| --- | --- | --- |
| `vercel-react-best-practices` | `vercel-labs/agent-skills` | Vercel 엔지니어링의 React·Next.js 성능 규칙 — C-TEC-001 |
| `web-design-guidelines` | `vercel-labs/agent-skills` | 접근성·UX 검토 — `UX-*` 태스크 15건 |
| `ai-sdk` | `vercel/ai` | AI SDK 공식 — C-TEC-005 · 006 |
| `shadcn` | `shadcn-ui/ui` | 컴포넌트 추가·디버깅 공식 — C-TEC-004 · D-08 |
| `supabase` | `supabase/agent-skills` | Supabase 전 제품 — C-TEC-003 |
| `supabase-postgres-best-practices` | `supabase/agent-skills` | Postgres 성능 — REQ-NF |
| `prisma-client-api` | `prisma/skills` | Prisma Client API 레퍼런스 |
| `prisma-database-setup` | `prisma/skills` | 프로바이더별 설정 — 로컬 Supabase 연결 |
| `tdd` | `mattpocock/skills` | 실패 시나리오를 테스트로 옮기는 절차 — DoD |
| `webapp-testing` | `anthropics/skills` | Playwright 기반 E2E — `TST-*` 태스크 |

```bash
npx skills add <owner/repo> --skill <name>   # 설치
npx skills list                              # 목록
npx skills update                            # 갱신
```

**채택하지 않은 것** — `vercel-optimize`(비용·성능 감사)는 운영 단계에 유용하나 구현 전이라 보류.
`code-review`는 Claude Code의 `/code-review`와 겹쳐 제외.

## 6. 하네스 샘플에서 버린 것

샘플은 Java/Spring · Kafka · Flutter 중심이다. 이 프로젝트와 겹치지 않는다.

| 버린 것 | 이유 |
| --- | --- |
| `300-java-spring` · `301-gradle` · `302-jpa-querydsl` · `303-database-mysql-jpa` | 스택 불일치 — Next.js + Prisma + PostgreSQL |
| `303-spring-redis` | **D-03이 캐시 서버를 금지**한다 |
| `304-kafka-data-pipeline` · `305-kafka-msa-saga` | **D-04가 메시지 큐를 금지**한다 |
| `302-python-fastapi` | 별도 백엔드 프로세스 금지 (D-01) |
| `306-react-vite-tailwind` | Vite SPA 전제 — App Router와 렌더링 모델이 다르다 |
| `307-flutter-riverpod-supabase` | 모바일 앱 없음 |
| `306-three-tier-architecture` | Spring 계층 전제. **계층 개념만 살려** `301-server-boundary-rules`로 다시 씀 |
| `304-api-rest-design` · `305-api-swagger-testing` | REST 서버 전제. Server Action·RSC에는 맞지 않음 |
| 서브에이전트 8종 | 전부 위 스택 대상 |
| `.claude/commands/` | 공식적으로 Skills에 통합됨 |

**가져와 다시 쓴 것** — `100` · `101` · `200` · `201` · `202`.
스택 무관한 프로세스라 뼈대는 유지하고 내용을 이 프로젝트 값으로 채웠다.
`102-gitflow-agent`는 `200`과 8할이 겹쳐 하나로 합쳤다.

## 7. 서브에이전트

| 에이전트 | 담당 | 주입 스킬 |
| --- | --- | --- |
| `nextjs-server` | Server Action · Route Handler · RSC · 캐시 | `301` · `300` · `vercel-react-best-practices` |
| `prisma-data` | 스키마 · 마이그레이션 · 쿼리 · RLS | `302` · `prisma-*` · `supabase-postgres-*` |
| `ai-gemini` | AI SDK · Gemini · 2단 파싱 | `303` · `ai-sdk` |
| `ui-shadcn` | 화면 · 컴포넌트 · 접근성 | `shadcn` · `web-design-guidelines` |

## 8. 유지보수

- **규칙이 바뀌면 원천 문서(SRS)를 먼저 고친다.** 규칙 파일은 SRS를 따라간다
- 새 스킬을 만들 때: 항상 참이면 `rules/`, 상황별이면 `skills/`
- 마켓플레이스 스킬은 `npx skills update`로 갱신한다. **직접 수정하지 않는다** — 갱신 시 덮어써진다
- 우리 규범과 외부 스킬이 충돌하면 **우리 규범이 이긴다.** 그 사실을 해당 스킬 문서에 적는다
