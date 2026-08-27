/**
 * 파싱·상태 픽스처 — 빈 상태(S6) / 구조화 필터 폴백(S7) / 오류(S8).
 *
 * 문구는 명세 §3의 확정 전문을 그대로 쓴다. 여기서 문장을 창작하지 않는다.
 * 톤 규약 — 시스템 탓을 사용자에게 돌리지 않고, 막다른 화면을 만들지 않는다.
 */
import type { FilterField, ResultView } from "./types";
import { QUERY } from "./top3";

/**
 * S6 — 결과 0건.
 * 반경까지 넓혀 봤다는 사실을 밝히고 다음 행동을 준다. 사유 없이 '없음'만 두지 않는다(SRS §6.3-6).
 */
export const EMPTY: Extract<ResultView, { kind: "empty" }> = {
  kind: "empty",
  query: QUERY,
  title: "조건에 맞는 곳을 못 찾았습니다",
  body: "반경 3km까지 넓혀 찾았습니다.",
  actions: [
    { label: "조건 줄이기", href: "/" },
    // 넓힌 결과임이 화면에 드러나야 한다 — N2 배너가 붙은 화면으로 보낸다
    { label: "반경 더 넓히기", href: "/results?fixture=notices" },
  ],
};

/** 폴백 화면의 구조화 필터. 필수 입력은 하나도 없다 (US-2 AC3). */
const FIELDS: FilterField[] = [
  { key: "area", label: "지역", options: ["강남역", "역삼", "선릉"] },
  { key: "party", label: "인원", options: ["1명", "2명", "3~4명"] },
  { key: "budget", label: "인당 예산", options: ["1만원 이하", "2만원 이하", "3만원 이하"] },
  { key: "situation", label: "상황", options: ["1인석", "조용", "콘센트"] },
  { key: "menu", label: "메뉴", options: ["국밥", "백반", "파스타"] },
];

/**
 * S7 — 자연어 해석 실패 → 구조화 필터로 전환.
 * 무엇을 못 알아들었는지 **그대로 보여 준다** (US-1 AC5 · 빈 화면 노출 0건).
 */
export const FALLBACK: Extract<ResultView, { kind: "fallback" }> = {
  kind: "fallback",
  query: "혼자 앉아도 안 뻘쭘한 데 2만원 이하",
  title: "이 표현은 아직 이해하지 못했습니다",
  unparsed: "안 뻘쭘한 데",
  fields: FIELDS,
};

/**
 * S8 — 오류.
 * '오류가 발생했습니다' 같은 책임 모호 표현을 쓰지 않는다. 무엇을 못 했는지 밝힌다.
 */
export const ERROR: Extract<ResultView, { kind: "error" }> = {
  kind: "error",
  title: "잠시 불러오지 못했습니다",
  body: "잠시 뒤 다시 시도해 주세요.",
  action: "다시 시도",
};
