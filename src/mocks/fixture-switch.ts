/**
 * ⚠️ 프로토타입 전용 · 본 개발 진입 시 **삭제한다.**
 *
 * SRS에 없는 개발용 장치다. `?fixture=` 로 화면 상태를 바꿔 보기 위한 것이며,
 * 이 프로토타입에서 유일하게 버리는 코드다. `src/mocks/` 밖으로 나가지 않게 한다.
 *
 * 경로 표는 docs/plan-docs/prototype-suggestion-local.md §8.
 */
import type { ResultView } from "./types";
import { NOTICES, QUERY, TOP3 } from "./top3";
import { EMPTY, ERROR, FALLBACK } from "./parse";

/** 명세 §1.1의 상태 7종(S2~S8) + §1.3의 확인용 프리셋 1개. S1은 `/` 이므로 여기 없다. */
export const FIXTURE_KEYS = [
  "loading",
  "ok",
  "stale",
  "two",
  "zero",
  "parse-fail",
  "error",
  "notices",
  "widened",
] as const;

export type FixtureKey = (typeof FIXTURE_KEYS)[number];

export const DEFAULT_FIXTURE: FixtureKey = "ok";

export function isFixtureKey(v: string | undefined): v is FixtureKey {
  return !!v && (FIXTURE_KEYS as readonly string[]).includes(v);
}

/** 스위처 UI에 띄우는 이름. 상태 번호를 붙여 명세 §1.1과 대조하기 쉽게 한다. */
export const FIXTURE_LABEL: Record<FixtureKey, string> = {
  loading: "S2 스켈레톤",
  ok: "S3 정상",
  stale: "S4 90일·가격",
  two: "S5 후보 2건",
  zero: "S6 0건",
  "parse-fail": "S7 폴백",
  error: "S8 오류",
  notices: "고지 배너 3종",
  widened: "반경 확대 결과",
};

export function resolveFixture(key: FixtureKey): ResultView {
  switch (key) {
    case "loading":
      return { kind: "loading" };
    case "ok":
      return { kind: "list", query: QUERY, candidates: [...TOP3.OK], notices: [] };
    case "stale":
      return { kind: "list", query: QUERY, candidates: [...TOP3.STALE], notices: [] };
    case "two":
      return { kind: "list", query: QUERY, candidates: [...TOP3.TWO], notices: [] };
    case "zero":
      return EMPTY;
    case "parse-fail":
      return FALLBACK;
    case "error":
      return ERROR;
    case "notices":
      // N1·N2가 동시에 걸린 상황이 실재한다 — 메뉴도 없고 반경도 넓힌 경우다.
      return {
        kind: "list",
        query: "감바스 먹을 곳",
        candidates: [...TOP3.OK],
        notices: [NOTICES.N1, NOTICES.N2, NOTICES.N3],
      };
    case "widened":
      // S6 의 '반경 더 넓히기' 착지 화면.
      // 질의를 그대로 유지하고 N2 만 얹는다 — notices 로 보내면 질의가 '감바스 먹을 곳'으로
      // 바뀌고 요청하지 않은 N1·N3 까지 딸려와 남의 검색에 착지한 것처럼 읽힌다.
      return {
        kind: "list",
        query: QUERY,
        candidates: [...TOP3.OK],
        notices: [NOTICES.N2],
      };
  }
}
