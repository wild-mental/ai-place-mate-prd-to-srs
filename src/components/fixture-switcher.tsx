/**
 * ⚠️ 프로토타입 전용 · 본 개발 진입 시 **삭제한다.**
 *
 * 화면 상태 8종을 눈으로 대조하기 위한 개발용 장치다. SRS에 없는 요소이므로
 * 제품 화면과 섞이지 않게 결과 아래 별도 영역에 두고 회색으로 낮춘다.
 */
import Link from "next/link";
import { FIXTURE_KEYS, FIXTURE_LABEL, type FixtureKey } from "@/mocks/fixture-switch";

export function FixtureSwitcher({ current }: { current: FixtureKey }) {
  return (
    <nav className="bg-muted mt-2 flex flex-col gap-2 rounded-lg px-3 py-3">
      <p className="text-muted-foreground text-[10px] tracking-wide uppercase">
        프로토타입 전용 · 화면 상태 전환
      </p>
      <div className="flex flex-wrap gap-1.5">
        {FIXTURE_KEYS.map((k) => (
          <Link
            key={k}
            href={`/results?fixture=${k}`}
            aria-current={k === current ? "page" : undefined}
            className={
              k === current
                ? "bg-foreground text-background rounded-sm px-2 py-1 text-[11px]"
                : "bg-background text-muted-foreground hover:text-foreground rounded-sm border px-2 py-1 text-[11px]"
            }
          >
            {FIXTURE_LABEL[k]}
          </Link>
        ))}
        {/* 선택은 fixture 가 아니라 파라미터다. 상태 목록을 늘리지 않고 확인만 연다 */}
        <Link
          href="/results?fixture=ok&selected=p2"
          className="bg-background text-muted-foreground hover:text-foreground rounded-sm border px-2 py-1 text-[11px]"
        >
          선택 상태
        </Link>
      </div>
    </nav>
  );
}
