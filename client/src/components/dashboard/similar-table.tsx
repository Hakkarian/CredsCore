"use client";

import { Trophy, Medal, Award } from "lucide-react";
import { EnrichedSimilarApplicant } from "@/lib/types";
import { MiniSparkline } from "./charts/mini-sparkline";

interface SimilarTableProps {
  data: EnrichedSimilarApplicant[];
}
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { cn } from "@/lib/utils";
import styles from "./similar-table.module.scss";

function getRankIcon(rank: number): React.ReactNode {
  if (rank === 1) return <Trophy className={styles.rankIconSvg} />;
  if (rank === 2) return <Medal className={styles.rankIconSvg} />;
  if (rank === 3) return <Award className={styles.rankIconSvg} />;
  return `#${rank}`;
}

function SimilarityBar({ score }: { score: number }) {
  const percentage = Math.round(score * 100);
  const level =
    percentage >= 75 ? "high" : percentage >= 50 ? "medium" : "low";

  const barColors: Record<string, string> = {
    high: styles.barHigh,
    medium: styles.barMedium,
    low: styles.barLow,
  };

  return (
    <div className={styles.barTrack}>
      <div
        className={cn(styles.barFill, barColors[level])}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}

function MatchBadge({ score }: { score: number }) {
  const percentage = Math.round(score * 100);
  const level =
    percentage >= 75 ? "high" : percentage >= 50 ? "medium" : "low";

  const badgeStyles: Record<string, string> = {
    high: styles.matchHigh,
    medium: styles.matchMedium,
    low: styles.matchLow,
  };

  const label = level === "high" ? "High Match" : level === "medium" ? "Medium Match" : "Low Match";

  return (
    <span className={cn(styles.matchBadge, badgeStyles[level])}>
      {label}
    </span>
  );
}

function RankBadge({ rank }: { rank: number }) {
  const rankStyles: Record<string, string> = {
    "1": styles.rank1,
    "2": styles.rank2,
    "3": styles.rank3,
  };

  return (
    <div
      className={cn(
        styles.rankBadge,
        rankStyles[String(rank)] ?? styles.rankDefault
      )}
    >
      {getRankIcon(rank)}
    </div>
  );
}

function SourceBadge({ sources }: { sources?: string[] }) {
  if (!sources?.length) return null;
  return (
    <div className={styles.sourceBadgeGroup}>
      {sources.map((source) => (
        <span
          key={source}
          className={cn(
            styles.sourceBadge,
            source === "fraud"
            ? styles.sourceFraud
            : source === "credit"
            ? styles.sourceCredit
            : styles.sourceDefault
          )}
        >
          {source}
        </span>
      ))}
    </div>
  );
}

const riskStyles: Record<string, string> = {
  high: styles.riskHigh,
  medium: styles.riskMedium,
  low: styles.riskLow,
};

export function SimilarTable({ data }: SimilarTableProps) {
  if (!data.length)
    return (
      <div className={styles.emptyState}>
        <p className={styles.emptyText}>Submit the form to see similar applicants</p>
      </div>
    );

  return (
    <ShimmerBorder className={styles.tableWrapper}>
        <h3 className={styles.tableTitle}>Similar Applicants</h3>
          <table className={styles.table}>
            <thead>
              <tr className={styles.tableHead}>
                <th className={styles.tableHeaderCell}>Rank</th>
                <th className={styles.tableHeaderCell}>Similarity</th>
                <th className={styles.tableHeaderCell}>Match</th>
                <th className={styles.tableHeaderCell}>Risk</th>
                <th className={styles.tableHeaderCell}>Default</th>
                <th className={styles.tableHeaderCell}>Index</th>
                <th className={styles.tableHeaderCell}>Source</th>
                <th className={styles.tableHeaderCell}>Trend</th>
              </tr>
            </thead>
            <tbody>
              {data.map((applicant, i) => (
                <tr key={i} className={styles.tableRow}>
                  <td className={styles.tableCell}>
                    <RankBadge rank={i + 1} />
                  </td>
                  <td className={styles.tableCell}>
                    <div className={styles.similarityCell}>
                      <span className={styles.similarityLabel}>
                        {Math.round(applicant.similarityScore * 100)}%
                      </span>
                      <SimilarityBar score={applicant.similarityScore} />
                    </div>
                  </td>
                  <td className={styles.tableCell}>
                    <MatchBadge score={applicant.similarityScore} />
                  </td>
                  <td className={styles.tableCell}>
                    <span
                      className={cn(styles.riskBadge, riskStyles[applicant.riskLevel] ?? styles.riskLow)}
                    >
                      {applicant.riskLevel}
                    </span>
                  </td>
                  <td className={styles.tableCell}>
                    <span
                      className={cn(styles.defaultBadge, applicant.defaultLabel ? styles.defaultBad : styles.defaultGood)}
                    >
                      {applicant.defaultLabel ? "Default" : "Good"}
                    </span>
                  </td>
                  <td className={styles.tableCellMono}>
                    #{applicant.index}
                  </td>
                  <td className={styles.tableCell}>
                    <SourceBadge sources={applicant.sources} />
                  </td>
                  <td className={styles.tableCell}>
                    <div className={styles.sparklineCell}>
                      <MiniSparkline
                        data={applicant.trendData ?? [{ value: 0.5 }, { value: applicant.similarityScore }]}
                        color={applicant.defaultLabel ? "#ef4444" : "#4ade80"}
                      />
                    </div>
                  </td>
                </tr>
              ))}
          </tbody>
          </table>
      </ShimmerBorder>
  );
}
