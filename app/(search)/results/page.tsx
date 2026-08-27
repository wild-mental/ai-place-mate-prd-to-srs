/**
 * 결과 페이지 — RNK-003 · 명세 §1.
 *
 * 상태 8종 중 S2~S8이 여기서 렌더된다(S1은 `/`). 어느 경로로 와도 빈 화면을 만들지 않는다.
 *
 * 로컬 프로토타입 범위다 — RSC의 실제 DB 조회 · `top3_rendered` 계측 · p95 실측은
 * 하지 않는다(로컬 최소안 §3·§9). Suspense 경계는 본 구현이 그대로 이어받을 자리로 남긴다.
 */
import { Suspense } from "react";
import Link from "next/link";
import { CandidateCard } from "@/components/candidate-card";
import { CompareTable } from "@/components/compare-table";
import { FixtureSwitcher } from "@/components/fixture-switcher";
import { NoticeBanner } from "@/components/notice-banner";
import {
  EmptyState,
  ErrorState,
  FallbackState,
  ResultSkeleton,
} from "@/components/result-states";
import {
  DEFAULT_FIXTURE,
  isFixtureKey,
  resolveFixture,
  type FixtureKey,
} from "@/mocks/fixture-switch";

async function ResultBody({
  fixture,
  selectedId,
}: {
  fixture: FixtureKey;
  selectedId?: string;
}) {
  const view = resolveFixture(fixture);

  if (view.kind === "loading") return <ResultSkeleton />;
  if (view.kind === "empty") return <EmptyState view={view} />;
  if (view.kind === "fallback") return <FallbackState view={view} />;
  if (view.kind === "error") return <ErrorState view={view} />;

  const top = view.notices.filter((n) => n.position === "top");
  const bottom = view.notices.filter((n) => n.position === "bottom");

  return (
    <div className="flex flex-col gap-4">
      {/* N1·N2 — 목록 상단. 결과가 어떻게 조정됐는지 먼저 밝힌다 */}
      <NoticeBanner notices={top} />

      <div className="flex flex-col gap-3">
        {view.candidates.map((c) => (
          <CandidateCard
            key={c.id}
            candidate={c}
            fixture={fixture}
            selected={c.id === selectedId}
          />
        ))}
      </div>

      {/* N3 — 목록 하단. 결과의 각주이지 전제가 아니다 */}
      <NoticeBanner notices={bottom} />

      <CompareTable candidates={view.candidates} />
    </div>
  );
}

export default async function ResultsPage({ searchParams }: PageProps<"/results">) {
  const sp = await searchParams;
  const raw = Array.isArray(sp.fixture) ? sp.fixture[0] : sp.fixture;
  const fixture = isFixtureKey(raw) ? raw : DEFAULT_FIXTURE;

  const typed = Array.isArray(sp.q) ? sp.q[0] : sp.q;
  const rawSelected = Array.isArray(sp.selected) ? sp.selected[0] : sp.selected;
  const view = resolveFixture(fixture);
  const hasQuery =
    view.kind === "list" || view.kind === "empty" || view.kind === "fallback";
  // S2·S8 은 질의를 되울리지 않는다. 불러오지 못한 화면에 조건을 적으면 결과처럼 읽힌다
  const query = hasQuery ? typed?.trim() || view.query : "";
  const selectedId =
    view.kind === "list" && view.candidates.some((c) => c.id === rawSelected)
      ? rawSelected
      : undefined;
  const selectedName =
    view.kind === "list"
      ? view.candidates.find((c) => c.id === selectedId)?.name
      : undefined;

  return (
    <main className="flex flex-col gap-4 px-4 py-6">
      <header className="flex flex-col gap-1.5">
        <Link
          href="/"
          className="text-muted-foreground text-xs underline underline-offset-4"
        >
          조건 다시 입력
        </Link>
        {/* 조건 없이 눌러도 결과가 나온다 — 그 사실이 화면에 드러나야 한다 (US-2 AC3) */}
        {hasQuery && (
          <h1 className="text-[15px] leading-snug font-semibold">
            {query || "조건 없이 찾은 결과"}
          </h1>
        )}
        {/* 여정의 마지막 칸이 닫혔음을 헤더에도 남긴다 (PRD 분기 02) */}
        {selectedName && (
          <p className="text-primary text-xs font-medium">
            1곳 선택함 · {selectedName}
          </p>
        )}
      </header>

      <Suspense fallback={<ResultSkeleton />}>
        <ResultBody fixture={fixture} selectedId={selectedId} />
      </Suspense>

      <FixtureSwitcher current={fixture} />
    </main>
  );
}
