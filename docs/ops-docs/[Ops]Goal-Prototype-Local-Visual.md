# [운영] `/goal` 프롬프트 — 로컬 시각 프로토타입

**문서 ID:** OPS-AIPLACE-GOAL-001

**개정 버전:** 1.1

**날짜:** 2026-08-27

**대상 작업:** [PROTO-AIPLACE-UI-002](../plan-docs/prototype-suggestion-local.md) — 태스크 8건 · 5영업일 · 1인

**화면 명세:** [SPEC-AIPLACE-PROTO-001](../plan-docs/%5BSpec%5DPrototype-Visual-Plan.md)

**결정 원장:** [`docs/grill/GRILL_LEDGER.md`](../grill/GRILL_LEDGER.md)

> 📝 **Claude Code `/goal` 에 붙여넣는 프롬프트다.** 아래 코드블록 전체를 그대로 복사해 쓴다.
> 완료 판정이 두 겹이다 — **기계 게이트 4종**(명령으로 판정)과 **aztks-agent 5축 전건 GO**(경험으로 판정). 둘 다 통과해야 끝난다.

---

## 프롬프트

```markdown
/goal

## 1) 작업 핵심 목표 및 범위
- 목표: `docs/plan-docs/prototype-suggestion-local.md`(PROTO-AIPLACE-UI-002)와 `docs/plan-docs/[Spec]Prototype-Visual-Plan.md`(SPEC-AIPLACE-PROTO-001)에 정의된 **로컬 시각 프로토타입 — 1동선 · 상태 8종 · 고지 배너 3종**을 구현하고, aztks-agent EVALUATE가 5축 전건 GO를 낼 때까지 개선한다.
- 시작 지점: 현재 브랜치 `docs/prototype-visual-plan` 에서 `feat/proto-local-visual` 브랜치를 새로 파고 시작한다.
- 작업 대상:
  - 신규 코드 — `app/layout.tsx`, `app/(search)/page.tsx`, `app/(search)/results/page.tsx`, `src/components/ui/`(shadcn 설치본), `src/mocks/{types,top3,parse,fixture-switch}.ts`, 프로젝트 루트 설정 파일
  - 스크린샷 산출물 — `reports/proto/`
  - 결정 기록 — `docs/grill/GRILL_LEDGER.md`
  - 태스크 8건 — `INF-001`(#1) `UX-001`(#2) `INF-002`(#3) `MCK-001`(#36) `UX-003`(#6) `UX-006`(#7) `UX-004`(#21) `RNK-003`(#47). **전부 부분 착수**이며 각 태스크의 범위는 로컬 최소안 §3 표의 왼쪽 열만이다.
- 작업 자율성: 사용자 승인을 기다리지 않고 종료 조건 도달까지 자율 진행한다. 단 **외부 계정 연결(Vercel·Supabase·Gemini)·배포·main 머지·force push는 금지**이므로 애초에 시도하지 않는다.

## 2) 작업 세부 규칙
- 스킬 `401-prototype-visual-rules` 를 먼저 읽고 그 규범 안에서 작업한다. 화면 값이 필요하면 `[Spec]Prototype-Visual-Plan.md` 를 직접 읽는다.
- 구현 순서는 로컬 최소안 §6의 D1~D5를 따른다:
  1) D1 `INF-001`·`UX-001`·`INF-002` — `create-next-app`(TS·App Router) + SRS §14.1 디렉터리 골격 + Tailwind 테마 + `shadcn init`
  2) D2 `MCK-001`·`UX-003` — 픽스처 + 조건 입력 화면
  3) D3 `UX-006` — Top-3 후보 카드 (명세 §2.1 슬롯 5개 순서 고정)
  4) D4 `UX-004` — 빈·오류·폴백 3화면 + `fixture-switch.ts`
  5) D5 `RNK-003` — 두 페이지 배선 · 스켈레톤 · 390px 정리 · 스크린샷
- 각 D 단계가 끝나면 커밋한다. 커밋 메시지는 한국어 Conventional Commits, 푸터에 `Refs #<이슈번호>`. **`Closes` 를 쓰지 않는다** — 부분 착수라 이슈가 닫히면 남은 범위가 사라진다.
- 화면은 `src/mocks/types.ts` 만 본다. 픽스처 리터럴(`top3.ts`·`parse.ts`)을 컴포넌트가 직접 import하지 않는다.
- D5 이후 `webapp-testing` 스킬(Playwright)로 **390px 폭** 스크린샷 9장을 `reports/proto/` 에 저장한다: `s1-input.png` `s2-loading.png` `s3-ok.png` `s4-stale.png` `s5-two.png` `s6-zero.png` `s7-parse-fail.png` `s8-error.png` `n-notices.png` `s9-selected.png`.
- 미해소 결정 처리 — `docs/grill/GRILL_LEDGER.md` 의 T3~T8은 아직 UNRESOLVED다. 구현 중 해당 결정이 필요해지면 **사용자에게 묻지 말고** 명세와 PRD(`docs/tech-design-docs/[PRD]AI-Place-Mate-PRD-v1_0.md` §2 페르소나 · §3 US-1~US-3)를 근거로 결정한 뒤 원장에 기록한다:
  - CORE(화면 구조·카피 틀·토큰 값·픽스처 실체) / MINOR(네이밍·간격·파일명)로 분류
  - 원장 상단에 grep 가능한 카운터를 각각 별도 줄로 유지 — `CORE: N` · `MINOR: M`
  - 각 항목에 `decision:` 과 `applied:` 를 남긴다

## 3) 종료 조건 및 종료 방법
- 종료 조건 (아래 중 하나라도 충족되는 순간 루프를 즉시 멈춘다):
  - 아래 **기계 게이트 4종이 모두 통과**하고, **동일 라운드에서 aztks-agent EVALUATE가 5축 전건 GO** → STOP REASON: AZTKS_GO
  - aztks-agent가 **연속 3회 NO-GO** → STOP REASON: EVAL_NOT_CONVERGING
  - 원장 `CORE` 카운터가 8에 도달 → STOP REASON: CORE_BUDGET
  - 원장 `MINOR` 카운터가 15에 도달 → STOP REASON: MINOR_BUDGET
  - 평가-진행 라운드(turn = /goal 평가자가 진행 상태를 한 번 점검하는 메인 에이전트 응답 사이클)가 누적 40회 도달 → STOP REASON: TURN_CAP (= or stop after 40 turns)
- 종료 방법:
  1) `docs/grill/GRILL_LEDGER.md` 마지막 줄에 `STOP REASON: <원인 코드>` 한 줄을 덧붙인다.
  2) `npm run build` 를 실행해 exit 0 출력을 대화에 남긴다. **[기계 게이트 1]**
  3) `npm run dev` 를 백그라운드로 띄운 뒤 아래를 실행해 **9줄 전부 `200`** 인 출력을 대화에 남긴다. **[기계 게이트 2]**
     `curl -s -o /dev/null -w "%{http_code} /\n" http://localhost:3000/ ; for f in loading ok stale two zero parse-fail error notices; do curl -s -o /dev/null -w "%{http_code} /results?fixture=$f\n" "http://localhost:3000/results?fixture=$f"; done`
  4) `grep -rnE '#[0-9a-fA-F]{3,8}' app/ src/ --include='*.tsx' | wc -l` 를 실행해 **`0`** 출력을 대화에 남긴다 (하드코딩 색상 0건 · INF-002 AC1). **[기계 게이트 3]**
  5) `ls app/layout.tsx 'app/(search)/page.tsx' 'app/(search)/results/page.tsx' src/mocks/types.ts src/mocks/fixture-switch.ts && ls reports/proto/ | wc -l` 를 실행해 exit 0 과 **`10`** 출력을 대화에 남긴다 (SRS §14.1 구조 + 스크린샷 10장). **[기계 게이트 4]**
  6) `cat docs/grill/GRILL_LEDGER.md | head -20` 를 실행해 `CORE: N` · `MINOR: M` 카운터 줄과 `STOP REASON:` 줄이 보이는 출력을 대화에 남긴다.
  7) 마지막 aztks-agent 스코어카드 전문(5축 각각의 GO/NO-GO와 사유)을 대화에 그대로 남긴다.
  8) `git log --oneline origin/main..HEAD` 와 `git status --porcelain` 를 실행해 커밋 목록과 변경 파일이 §1 작업 대상 안에만 있음을 대화에 남긴다.

## 4) 기타 제약조건
- main 머지 금지 · force push 금지 · 배포 금지. Vercel·Supabase·Gemini 어느 것도 연결하지 않는다.
- 수정 금지 — `docs/plan-docs/[TaskList]AI-Place-Mate-Task-List.md`, `docs/plan-docs/[Plan]*.md`(생성물이다), `docs/tech-design-docs/**`, `docs/source-docs/**`, `tools/**`.
- `docs/tasks/*.md` 는 **완료한 체크박스만** 체크한다. 미완 체크박스를 지우지 않는다. GitHub 이슈를 닫지 않는다.
- 로컬 최소안 §9를 지킨다 — **테스트 코드·계측 코드·DB/AI/인증 연동을 만들지 않는다.** 성능·접근성을 검증했다고 말하지 않는다.
- `src/modules/` 와 `src/lib/` 는 디렉터리만 만들고 **비워 둔다.** 본 개발이 채운다.
- shadcn/ui에 있는 컴포넌트를 직접 작성하지 않는다 (D-08 · REQ-TEC-007).
- §1 작업 대상 밖 파일을 수정하지 않는다.

## 5) aztks-agent 평가 규약
- 호출 시점: **D5까지 한 바퀴 끝나고 기계 게이트 4종이 모두 통과한 뒤에만** 호출한다. 구현 중간에는 호출하지 않는다.
- 호출 방식: `subagent_type: "aztks-agent"` · 프롬프트 첫 줄에 `MODE: EVALUATE` · read-only.
- 평가자에게 넘길 입력 (경로를 프롬프트에 명시):
  - 스크린샷 10장 — `reports/proto/*.png`
  - 화면 명세 — `docs/plan-docs/[Spec]Prototype-Visual-Plan.md`
  - 제품 근거 — `docs/tech-design-docs/[PRD]AI-Place-Mate-PRD-v1_0.md` §2 핵심 페르소나(C2·C3·C4·C1) · §2.2 v0.1이 만드는 흐름 · §3 US-1~US-3
  - 구현 코드 — `app/(search)/**`, `src/mocks/**`
- 5축 판정 앵커 (이 앵커로만 GO/NO-GO를 매기게 한다):

  | 축 | GO 조건 |
  | --- | --- |
  | **알아서(coverage)** | 상태 8종(S1~S8)과 고지 배너 3종(N1·N2·N3)이 전건 존재하고, N1·N2 동시 노출이 `?fixture=notices` 에서 확인된다. 카드 슬롯 ⑥(선택 행위)이 `?selected=` 로 성립한다 |
  | **잘(quality)** | 모든 후보 카드에 근거 4항목(선정 이유·근거 속성·확인 일자·확인 주체)이 표기율 100%다. 판정형 문구 0건. 인당 예상가가 범위로 표기되고 부실 시 '가격 확인 필요'다 |
  | **딱(coherence)** | C2(예산 역산)·C3(메뉴명 한 번)·C4(가기 전 판단) 세 페르소나의 여정이 `/` → `/results` 2페이지 안에서 끊기지 않는다. PRD §2.2 흐름의 분기 01·02가 화면으로 성립한다 |
  | **깔끔(clarity)** | 390px에서 가로 스크롤 0건. 비교표 값이 5자 이내. 카드 슬롯 순서가 세 장 모두 동일 |
  | **센스(consumability)** | 빈 화면 0건. 막다른 상태(S6·S7·S8)마다 다음 행동이 있다. 오류 문구가 사용자 탓으로 읽히지 않는다 |

- NO-GO가 나오면 **지적된 축만** 고치고 기계 게이트 4종을 다시 통과시킨 뒤 재평가한다. 라운드마다 스크린샷을 다시 찍는다.
- 평가자의 판정을 임의로 뒤집지 않는다. 앵커 자체가 틀렸다고 판단되면 고치지 말고 **그 사실을 원장에 기록하고 STOP** 한다.
```

---

## 붙여넣기 전에 조정할 수 있는 값

| 값 | 현재 | 조정 판단 |
| --- | --- | --- |
| turn cap | **40** | 5일치 작업 + 평가 라운드를 감안한 값. 짧게 끝내려면 25~30 |
| `CORE` budget | **8** | 원장의 미해소 토픽 T3~T8이 6건이라 여유 2를 얹었다. 결정을 직접 내리고 싶으면 6으로 낮춰 조기 정지 |
| `MINOR` budget | **15** | 네이밍·간격 수준. 넉넉한 편이다 |
| 연속 NO-GO 한도 | **3** | 평가가 수렴하지 않을 때의 탈출구 |
| 시작 브랜치 | `docs/prototype-visual-plan` | 화면 명세가 이 브랜치에 있다. main에 머지한 뒤라면 `main` 으로 바꾼다 |

## 왜 완료 판정을 두 겹으로 두었나

기계 게이트만 두면 **화면이 뜨기만 해도 통과**한다. aztks-agent만 두면 판정이 라운드마다 흔들린다.
그래서 앞의 넷은 명령으로, 마지막 하나는 **5축 앵커로 고정한 평가**로 나눴다. 앵커를 표로 못 박은 이유도 같다 —
"충분한 사용자 경험"은 그대로 두면 측정할 수 없고, 평가자마다 다른 답을 낸다.

---

**OPS-AIPLACE-GOAL-001 · v1.1 · 2026-08-27 · 기계 게이트 4종 + AZTKS 5축 · turn cap 40**

> v1.1 — 스크린샷 9장 → **10장**. 1라운드 평가에서 카드 슬롯 ⑥(선택 행위) 누락이 잡혀 명세 §2.1이 늘었고, 그 화면(`s9-selected.png`)이 캡처 대상에 더해졌다. 게이트는 산출물 수를 세는 장치이지 품질 기준이 아니므로, 명세가 늘면 함께 늘린다.
