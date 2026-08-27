/**
 * 비교표 — 명세 §2.2.
 *
 * 축 4개가 고정이다: 인당가 · 대표메뉴 · 상황속성 · 확인일자 (PRD §2.2 T3 노드).
 * 라벨 열 56px + 후보 열 등분. **가로 스크롤을 만들지 않는다** —
 * 넘치면 폰트를 줄이지 말고 값을 줄인다(픽스처의 compare 값이 최대 5자다).
 *
 * 후보가 2건이면 2열로 줄어든다. 빈 열을 만들지 않는다 (SRS §6.3-3).
 */
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Candidate, CompareCell } from "@/mocks/types";

const AXES: { key: keyof CompareCell; label: string }[] = [
  { key: "price", label: "인당가" },
  { key: "signature", label: "대표" },
  { key: "situation", label: "상황" },
  { key: "verified", label: "확인" },
];

export function CompareTable({ candidates }: { candidates: Candidate[] }) {
  return (
    <section className="flex flex-col gap-2">
      <h2 className="text-muted-foreground text-xs font-medium">같은 축으로 비교</h2>
      <Table className="table-fixed text-[12px]">
        <TableHeader>
          <TableRow>
            <TableHead className="text-muted-foreground h-8 w-14 px-2 text-[11px]">

            </TableHead>
            {candidates.map((c) => (
              <TableHead key={c.id} className="h-8 px-2 text-[11px] tabular-nums">
                {c.rank}번
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {AXES.map((axis) => (
            <TableRow key={axis.key}>
              <TableCell className="text-muted-foreground w-14 px-2 py-1.5 text-[11px]">
                {axis.label}
              </TableCell>
              {candidates.map((c) => {
                // 90일 경과 후보는 확인일자 칸에 표식을 덧붙인다
                const stale =
                  axis.key === "verified" && c.verifications.some((v) => v.stale);
                return (
                  <TableCell
                    key={c.id}
                    className={`truncate px-2 py-1.5 tabular-nums ${stale ? "text-warn" : ""}`}
                  >
                    {c.compare[axis.key]}
                    {stale && " ⚠"}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </section>
  );
}
