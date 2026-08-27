/**
 * 고지 배너 — 명세 §1.2.
 *
 * **상태가 아니라 요소다.** 정상 결과 위에 얹히고 둘 이상 동시에 뜬다(N1·N2).
 * 시스템이 요청을 그대로 처리하지 않고 조정했을 때 그 사실을 밝히는 자리이며,
 * 조정해 놓고 밝히지 않는 것은 근거를 빼는 것과 같다 — PRD가 셋 다 표기율 100%를 걸었다.
 *
 * **오류가 아니다.** 경고·오류 색을 쓰지 않는다.
 */
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { Notice } from "@/mocks/types";

export function NoticeBanner({ notices }: { notices: Notice[] }) {
  if (notices.length === 0) return null;

  return (
    // 둘 이상이면 스택으로 쌓는다
    <div className="flex flex-col gap-1.5">
      {notices.map((n) => (
        <Alert
          key={n.id}
          className="text-notice bg-notice-bg border-notice-border px-3 py-2"
        >
          <AlertDescription className="text-notice text-[12px] leading-snug">
            {n.text}
          </AlertDescription>
        </Alert>
      ))}
    </div>
  );
}
