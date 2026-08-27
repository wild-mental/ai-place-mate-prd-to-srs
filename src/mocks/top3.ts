/**
 * Top-3 픽스처 — 정상 / 90일경과·가격부실 / 후보 2건 / 0건.
 *
 * 매장명·메뉴·가격은 전부 **합성 데이터**다 (MCK-001 보안 제약).
 * 상권은 서울 강남역 반경 1km를 가정한다 — C3(마케터 점심)·C2(대학원생)·C4(프리랜서)가
 * 겹치는 밀집 상권이라 픽스처가 현실적으로 읽힌다.
 *
 * 픽스처는 정상보다 실패·경계를 더 많이 담는다 — 그쪽이 실제 데이터로 만들기 어렵다.
 */
import type { Candidate, Notice } from "./types";

/** 화면 전반에서 쓰는 기본 질의. C2(예산)·C4(1인석) 조건이 함께 걸린 문장이다. */
export const QUERY = "혼자 조용히 밥 먹을 곳, 2만원 이하";

/**
 * 확인 주체 4종이 한 화면에 모두 보이도록 배치했다.
 * 확인 이력이 속성 단위이므로 카드 3장으로 4종을 덮을 수 있다.
 */
const OK: Candidate[] = [
  {
    id: "p1",
    rank: 1,
    name: "무쇠솥 한상",
    priceRange: { min: 11000, max: 14000 },
    reason: "1인석 6석 · 21시까지 영업 — 조건 3개 중 3개 충족",
    attributes: ["1인석", "늦은 영업", "국밥"],
    verifications: [
      { attribute: "1인석", at: "2026-08-12", by: "매장 등록", stale: false },
      { attribute: "영업시간", at: "2026-07-28", by: "운영자 검증", stale: false },
    ],
    compare: { price: "1.4만", signature: "국밥", situation: "1인석", verified: "7/28" },
  },
  {
    id: "p2",
    rank: 2,
    name: "온기식당",
    priceRange: { min: 15000, max: 18000 },
    reason: "1인석 4석 · 소음 낮음 — 조건 3개 중 2개 충족",
    attributes: ["1인석", "조용", "백반"],
    verifications: [
      { attribute: "1인석", at: "2026-08-20", by: "후기 코멘트", stale: false },
    ],
    compare: { price: "1.8만", signature: "백반", situation: "조용", verified: "8/20" },
  },
  {
    id: "p3",
    rank: 3,
    name: "느린한끼",
    priceRange: { min: 16000, max: 19000 },
    reason: "콘센트 좌석 12석 · 체류 제한 없음 — 조건 3개 중 2개 충족",
    attributes: ["콘센트", "체류 자유", "파스타"],
    verifications: [
      { attribute: "좌석", at: "2026-08-05", by: "자동 수집", stale: false },
    ],
    compare: { price: "1.9만", signature: "파스타", situation: "콘센트", verified: "8/05" },
  },
];

/**
 * S4 — 90일 경과 경고 + 가격 확인 필요.
 * 1번은 가격 표본이 부실해 예상가 대신 '가격 확인 필요'가 뜨고 예산 필터 판정에서 빠진다(US-1 AC6).
 * 3번은 좌석 정보가 90일 넘게 갱신되지 않아 경고가 붙는다(US-3 AC2 · 경고 누락률 0%).
 */
const STALE: Candidate[] = [
  {
    ...OK[0],
    priceRange: null,
    verifications: [
      { attribute: "1인석", at: "2026-08-12", by: "매장 등록", stale: false },
      { attribute: "가격", at: "2026-05-03", by: "자동 수집", stale: true },
    ],
    compare: { ...OK[0].compare, price: "확인필요", verified: "5/03" },
  },
  OK[1],
  {
    ...OK[2],
    verifications: [
      { attribute: "좌석", at: "2026-04-18", by: "자동 수집", stale: true },
    ],
    compare: { ...OK[2].compare, verified: "4/18" },
  },
];

/** S5 — 후보 2건. 3건을 억지로 채우지 않는다 (SRS §6.3-3). 비교표도 2열로 줄어든다. */
const TWO: Candidate[] = [OK[0], OK[1]];

/** 고지 배너 3종 — 명세 §1.2. N1·N2는 동시에 성립한다. */
export const NOTICES: Record<Notice["id"], Notice> = {
  N1: {
    id: "N1",
    text: "찾는 메뉴가 없어 유사 메뉴로 대체했습니다",
    position: "top",
  },
  N2: { id: "N2", text: "반경을 3km로 넓혔습니다", position: "top" },
  N3: { id: "N3", text: "예산 초과 4곳은 제외했습니다", position: "bottom" },
};

export const TOP3 = { OK, STALE, TWO } as const;
