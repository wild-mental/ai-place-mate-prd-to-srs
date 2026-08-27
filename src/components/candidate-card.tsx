/**
 * 후보 카드 — UX-006 · 명세 §2.1.
 *
 * 슬롯 5개의 **순서가 고정**이다. 세 장이 같은 항목을 같은 자리에 두어야
 * 눈이 세 장을 훑을 수 있다. 카드마다 순서를 바꾸지 않는다.
 *
 * 근거 4항목(선정 이유·근거 속성·확인 일자·확인 주체) 중 하나라도 없으면
 * 카드가 될 수 없다 (SRS §6.3-2).
 */
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { Candidate, PriceRange } from "@/mocks/types";

/** 인당 예상가는 **범위로만** 쓴다. 단일 값으로 쓰지 않는다 (US-1 AC1 · 범위 폭 ≤ ±20%). */
function formatPrice(range: PriceRange): string | null {
  if (!range) return null;
  const man = (won: number) => (won / 10000).toFixed(1);
  return `${man(range.min)}~${man(range.max)}만`;
}

/** 카드에는 M/D 로 축약해 표기한다. */
function formatDate(iso: string): string {
  const [, m, d] = iso.split("-");
  return `${Number(m)}/${d}`;
}

export function CandidateCard({ candidate }: { candidate: Candidate }) {
  const price = formatPrice(candidate.priceRange);
  const stale = candidate.verifications.some((v) => v.stale);

  return (
    <Card className="gap-0 py-4">
      <CardContent className="flex flex-col gap-2.5 px-4">
        {/* ① 순위 · 매장명 · 인당 예상가 범위 */}
        <div className="flex items-baseline justify-between gap-2">
          <h3 className="flex items-baseline gap-1.5 text-[15px] font-semibold">
            <span className="text-muted-foreground text-xs tabular-nums">
              {candidate.rank}
            </span>
            {candidate.name}
          </h3>
          {price ? (
            <span className="shrink-0 text-[13px] font-medium tabular-nums">
              {price}
            </span>
          ) : (
            // 없는 정확도를 있는 것처럼 보이게 하지 않는다 (US-1 AC6)
            <span className="text-muted-foreground shrink-0 text-[13px]">
              가격 확인 필요
            </span>
          )}
        </div>

        {/* ② 선정 이유 1줄 — 문장 틀 고정: <속성 나열> — 조건 N개 중 M개 충족 */}
        <p className="text-[13px] leading-relaxed">{candidate.reason}</p>

        {/* ③ 근거 속성 */}
        <div className="flex flex-wrap gap-1">
          {candidate.attributes.map((a) => (
            <Badge key={a} variant="secondary" className="rounded-sm font-normal">
              {a}
            </Badge>
          ))}
        </div>

        {/* ④ 90일 경과 경고 — 조건부 슬롯이다. 없으면 빈 줄을 남기지 않는다 */}
        {stale && (
          <p className="text-warn border-warn-border bg-warn-bg rounded-sm border px-2 py-1 text-xs">
            확인 90일 경과
          </p>
        )}

        {/* ⑤ 확인 일자 · 확인 주체 — 확인 이력은 속성 단위다 (US-3 AC2) */}
        <ul className="text-evidence flex flex-col gap-0.5 text-[11px]">
          {candidate.verifications.map((v) => (
            <li key={v.attribute} className="flex gap-1.5 tabular-nums">
              <span className="text-muted-foreground">{v.attribute}</span>
              <span>
                {formatDate(v.at)} · {v.by}
              </span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
