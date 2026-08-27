/**
 * 상태 화면 — UX-004 · 명세 §1.1 (S2 · S6 · S7 · S8).
 *
 * 어느 상태에서도 **빈 화면을 만들지 않는다**(SRS §6.3-6).
 * 막다른 상태에는 반드시 다음 행동을 준다. 문구는 명세 §3의 확정 전문을 그대로 쓴다.
 */
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import type { ResultView } from "@/mocks/types";

/** S2 — 로딩 스켈레톤. 결과 카드의 **골격**을 미리 보여 준다. 흰 화면을 주지 않는다. */
export function ResultSkeleton() {
  return (
    <div className="flex flex-col gap-3" aria-label="결과를 불러오는 중">
      {[0, 1, 2].map((i) => (
        <div key={i} className="flex flex-col gap-2.5 rounded-xl border p-4">
          <div className="flex justify-between">
            <Skeleton className="h-4 w-28" />
            <Skeleton className="h-4 w-14" />
          </div>
          <Skeleton className="h-3 w-full" />
          <div className="flex gap-1">
            <Skeleton className="h-5 w-12 rounded-sm" />
            <Skeleton className="h-5 w-16 rounded-sm" />
            <Skeleton className="h-5 w-10 rounded-sm" />
          </div>
          <Skeleton className="h-2.5 w-32" />
        </div>
      ))}
    </div>
  );
}

/** S6 — 결과 0건. 사유와 다음 행동을 함께 준다. 막다른 화면을 만들지 않는다. */
export function EmptyState({ view }: { view: Extract<ResultView, { kind: "empty" }> }) {
  return (
    <section className="flex flex-col items-start gap-3 rounded-xl border border-dashed px-4 py-8">
      <h2 className="text-[15px] font-semibold">{view.title}</h2>
      <p className="text-empty text-[13px]">{view.body}</p>
      {/* 다음 행동은 실제로 갈 곳이 있어야 한다. 눌러도 아무 일이 없으면 막다른 화면과 같다 */}
      <div className="mt-1 flex flex-wrap gap-2">
        {view.actions.map((a, i) => (
          <Button key={a} asChild variant="outline" size="sm">
            <Link href={i === 0 ? "/" : "/results?fixture=ok"}>{a}</Link>
          </Button>
        ))}
      </div>
    </section>
  );
}

/**
 * S7 — 자연어 해석 실패 → 구조화 필터로 전환.
 * **해석하지 못한 표현을 그대로 표기한다** (US-1 AC5). 무엇을 못 알아들었는지 알려 준다.
 */
export function FallbackState({
  view,
}: {
  view: Extract<ResultView, { kind: "fallback" }>;
}) {
  return (
    <form action="/results" method="get" className="flex flex-col gap-4">
      <div className="flex flex-col gap-2 rounded-xl border px-4 py-4">
        <h2 className="text-[15px] font-semibold">{view.title}</h2>
        <p className="text-[13px]">
          <span className="bg-muted rounded-sm px-1.5 py-0.5 font-medium">
            {view.unparsed}
          </span>
          <span className="text-empty"> — 아래에서 직접 골라 주세요</span>
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {view.fields.map((f) => (
          <div key={f.key} className="flex flex-col gap-1.5">
            <span className="text-muted-foreground text-xs">{f.label}</span>
            <Select name={f.key}>
              <SelectTrigger className="w-full" size="sm">
                <SelectValue placeholder="상관없음" />
              </SelectTrigger>
              <SelectContent>
                {f.options.map((o) => (
                  <SelectItem key={o} value={o}>
                    {o}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        ))}
      </div>

      <Button type="submit" className="w-full">
        이 조건으로 다시 찾기
      </Button>
    </form>
  );
}

/** S8 — 오류. 시스템 탓을 사용자에게 돌리지 않는다. 되돌아갈 길을 준다. */
export function ErrorState({ view }: { view: Extract<ResultView, { kind: "error" }> }) {
  return (
    <section className="flex flex-col items-start gap-3 rounded-xl border px-4 py-8">
      <h2 className="text-[15px] font-semibold">{view.title}</h2>
      <p className="text-empty text-[13px]">{view.body}</p>
      <Button asChild variant="outline" size="sm" className="mt-1">
        <Link href="/results?fixture=ok">{view.action}</Link>
      </Button>
    </section>
  );
}
