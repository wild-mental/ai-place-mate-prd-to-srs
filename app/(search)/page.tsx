/**
 * S1 조건 입력 — UX-003.
 *
 * 확인 포인트: **필수 입력 필드 0개**로 검색이 된다 (US-2 AC3 · 입력 단계 ≤ 1회).
 * 자연어 1줄과 구조화 조건을 한 화면에서 받는다. 조건을 여러 화면에 나눠 받지 않는다.
 */
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

/** 구조화 조건 5종. 전부 선택이며 기본값이 '상관없음'이다. S7 폴백 필터와 같은 집합이다. */
const CONDITIONS = [
  { name: "area", label: "지역", options: ["강남역", "역삼", "선릉"] },
  { name: "party", label: "인원", options: ["1명", "2명", "3~4명"] },
  { name: "budget", label: "인당 예산", options: ["1만원 이하", "2만원 이하", "3만원 이하"] },
  { name: "situation", label: "상황", options: ["1인석", "조용", "콘센트"] },
  // C3(메뉴명 한 번)이 자연어 필드에만 의존하지 않게 한다 (US-2 AC1)
  { name: "menu", label: "메뉴", options: ["국밥", "백반", "파스타"] },
];

export default function ConditionPage() {
  return (
    <main className="flex flex-col gap-6 px-4 py-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-[22px] leading-snug font-semibold tracking-tight text-balance">
          조건을 말하면
          <br />
          근거가 붙은 세 곳이 옵니다
        </h1>
        <p className="text-muted-foreground text-sm">
          왜 그곳인지 확인 일자까지 함께 보여 드립니다.
        </p>
      </header>

      <form action="/results" method="get" className="flex flex-col gap-5">
        <div className="flex flex-col gap-2">
          <Label htmlFor="q" className="text-sm">
            조건을 한 줄로 적어 보세요
          </Label>
          <Input
            id="q"
            name="q"
            placeholder="예: 혼자 조용히 밥 먹을 곳, 2만원 이하"
            autoComplete="off"
          />
        </div>

        <fieldset className="flex flex-col gap-3">
          <legend className="text-muted-foreground mb-1 text-xs">
            골라도 되고, 안 골라도 됩니다
          </legend>
          <div className="grid grid-cols-2 gap-3">
            {CONDITIONS.map((c) => (
              <div key={c.name} className="flex flex-col gap-1.5">
                <Label htmlFor={c.name} className="text-muted-foreground text-xs">
                  {c.label}
                </Label>
                <Select name={c.name}>
                  <SelectTrigger id={c.name} className="w-full" size="sm">
                    <SelectValue placeholder="상관없음" />
                  </SelectTrigger>
                  <SelectContent>
                    {c.options.map((o) => (
                      <SelectItem key={o} value={o}>
                        {o}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ))}
          </div>
        </fieldset>

        {/* 필수 입력 0개를 화면으로 증명하는 지점 — 아무것도 채우지 않고 눌러도 결과가 나온다 */}
        <Button type="submit" className="w-full">
          근거와 함께 보기
        </Button>
        <p className="text-muted-foreground -mt-2 text-center text-xs">
          아무것도 입력하지 않아도 결과를 받습니다
        </p>
      </form>

      <Link
        href="/results?fixture=ok"
        className="text-muted-foreground mt-2 text-center text-xs underline underline-offset-4"
      >
        화면 상태 8종 둘러보기
      </Link>
    </main>
  );
}
