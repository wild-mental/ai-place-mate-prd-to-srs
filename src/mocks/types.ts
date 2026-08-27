/**
 * 화면이 소비하는 타입 한 겹.
 *
 * 컴포넌트는 이 파일만 본다. 픽스처 리터럴(top3.ts · parse.ts)을 직접 물지 않는다.
 * `CTR-001` 이 확정되면 이 파일 하나를 계약 타입으로 갈아 끼우고 화면은 그대로 둔다.
 *
 * 근거: docs/plan-docs/[Spec]Prototype-Visual-Plan.md §2
 */

/** 근거 4항목의 '확인 주체'. 명세 §2.3 — 이 넷 외의 값을 만들지 않는다. */
export type VerificationSource =
  | "매장 등록" // MCH-004 사장이 콘솔에서 입력
  | "후기 코멘트" // EVD-005 방문 후 입력 · 불일치 신고
  | "운영자 검증" // DAT-010 재확인 큐 처리
  | "자동 수집"; // DAT-006 색인 파이프라인

/**
 * 확인 이력은 **속성 단위**다.
 * US-3 AC2가 "어떤 속성이 90일 이상 갱신되지 않았고, 그 속성이 카드에 노출되면"이라고
 * 못 박고 있으므로 카드 전체가 아니라 속성마다 확인 일자·주체가 붙는다.
 */
export type Verification = {
  /** 무엇을 확인했나 — '1인석' '영업시간' '가격' */
  attribute: string;
  /** ISO 날짜. 카드에는 M/D 로 축약해 표기한다 */
  at: string;
  by: VerificationSource;
  /** 90일 경과 여부. 하나라도 true면 카드에 경고가 붙는다 (US-3 AC2 · 경고 누락률 0%) */
  stale: boolean;
};

/** 인당 예상가 범위. null 이면 '가격 확인 필요' (US-1 AC6) */
export type PriceRange = { min: number; max: number } | null;

/** 비교표 한 열. 값은 **최대 5자** — 명세 §2.2. 넘치면 폰트가 아니라 값을 줄인다. */
export type CompareCell = {
  price: string;
  signature: string;
  situation: string;
  verified: string;
};

export type Candidate = {
  id: string;
  rank: number;
  name: string;
  priceRange: PriceRange;
  /**
   * 선정 이유 1줄 — 근거 4항목 ①.
   * 문장 틀이 고정이다: `<속성 나열> — 조건 N개 중 M개 충족`.
   * 판정어를 넣을 자리가 없게 만든 틀이다 (SRS §6.3-4 · US-3 AC2 판정형 문구 0건).
   */
  reason: string;
  /** 근거 속성 — 근거 4항목 ②. 칩으로 나열한다 */
  attributes: string[];
  /** 확인 일자 · 확인 주체 — 근거 4항목 ③④ */
  verifications: Verification[];
  compare: CompareCell;
};

/**
 * 고지 배너 — 명세 §1.2.
 * 상태가 아니라 요소다. 정상 결과(S3·S4·S5) 위에 얹히고 둘 이상 동시에 뜬다.
 */
export type Notice = {
  id: "N1" | "N2" | "N3";
  text: string;
  /** N1·N2는 목록 상단, N3는 하단. N3는 결과의 각주이지 전제가 아니다 */
  position: "top" | "bottom";
};

/** 폴백 화면(S7)의 구조화 필터 한 줄 */
export type FilterField = {
  key: string;
  label: string;
  options: string[];
};

/** 화면 상태 8종 — 명세 §1.1. 한 번에 하나만 성립한다. */
export type ResultView =
  | { kind: "loading" } // S2
  | {
      kind: "list"; // S3 · S4 · S5
      query: string;
      candidates: Candidate[];
      notices: Notice[];
    }
  | {
      kind: "empty"; // S6
      query: string;
      title: string;
      body: string;
      /** 다음 행동. 인덱스로 목적지를 유추하지 않는다 — 항목이 늘면 조용히 어긋난다 */
      actions: { label: string; href: string }[];
    }
  | {
      kind: "fallback"; // S7
      query: string;
      title: string;
      /** 해석하지 못한 표현을 그대로 표기한다 (US-1 AC5) */
      unparsed: string;
      fields: FilterField[];
    }
  | {
      kind: "error"; // S8
      title: string;
      body: string;
      action: string;
    };
