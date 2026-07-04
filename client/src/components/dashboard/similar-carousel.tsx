"use client";

import { useRef } from "react";
import { Trophy, Medal, Award, ChevronLeft, ChevronRight } from "lucide-react";
import { EnrichedSimilarApplicant } from "@/lib/types";
import { MiniSparkline } from "@/components/dashboard/charts";

interface SimilarCarouselProps {
  data: EnrichedSimilarApplicant[];
}
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { cn } from "@/lib/utils";
import styles from "./similar-carousel.module.scss";

function getRankIcon(rank: number): React.ReactNode {
  if (rank === 1) return <Trophy className={styles.rankIconSvg} />;
  if (rank === 2) return <Medal className={styles.rankIconSvg} />;
  if (rank === 3) return <Award className={styles.rankIconSvg} />;
  return `#${rank}`;
}

function CircularProgress({ score }: { score: number }) {
  const percentage = Math.round(score * 100);
  const level =
    percentage >= 75 ? "high" : percentage >= 50 ? "medium" : "low";

  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const strokeColors: Record<string, string> = {
    high: "#4ade80",
    medium: "#facc15",
    low: "#ef4444",
  };

  return (
    <div className={styles.progressContainer}>
      <svg viewBox="0 0 100 100" className={styles.progressSvg}>
        <circle
          className={styles.progressTrack}
          cx="50"
          cy="50"
          r="45"
          strokeWidth="6"
        />
        <circle
          className={styles.progressFill}
          cx="50"
          cy="50"
          r="45"
          strokeWidth="6"
          strokeLinecap="round"
          stroke={strokeColors[level]}
          style={{
            strokeDasharray: circumference,
            strokeDashoffset,
          }}
        />
      </svg>
      <div className={styles.progressCenter}>
        <span className={styles.progressPercent}>{percentage}%</span>
        <span className={styles.progressLabel}>match</span>
      </div>
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

const riskTextStyles: Record<string, string> = {
  high: styles.riskTextHigh,
  medium: styles.riskTextMedium,
  low: styles.riskTextLow,
};

export function SimilarCarousel({ data }: SimilarCarouselProps) {
  const trackRef = useRef<HTMLDivElement>(null);

  if (!data.length)
    return (
      <div className={styles.emptyState}>
        <p className={styles.emptyText}>Submit the form to see similar applicants</p>
      </div>
    );

  const scrollByCard = (direction: "prev" | "next") => {
    if (trackRef.current) {
      const cardWidth = 280; // min-width + gap
      const scrollAmount = direction === "next" ? cardWidth : -cardWidth;
      trackRef.current.scrollBy({ left: scrollAmount, behavior: "smooth" });
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.carouselNav}>
        <h3 className={styles.carouselTitle}>Similar Applicants</h3>
      </div>
      <div className={styles.carouselWrapper}>
        <div className={styles.carouselTrack} ref={trackRef}>
          {data.map((applicant, i) => (
            <ShimmerBorder key={i} className={styles.applicantCardOuter} borderRadius="0.75rem">
              <div className={styles.applicantCard}>
                <div className={styles.cardHeader}>
                  <RankBadge rank={i + 1} />
                  <MatchBadge score={applicant.similarityScore} />
                </div>

                <div className={styles.progressCenterArea}>
                  <CircularProgress score={applicant.similarityScore} />
                </div>

                <div className={styles.statusRow}>
                  <span className={styles.statusLabel}>Status</span>
                  <span
                    className={cn(styles.statusBadge, applicant.defaultLabel ? styles.statusDefault : styles.statusGood)}
                  >
                    {applicant.defaultLabel ? "Default" : "Good"}
                  </span>
                </div>

                <div className={styles.metricsSection}>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Risk Level</span>
                    <span
                      className={cn(styles.metricValue, riskTextStyles[applicant.riskLevel] ?? styles.riskTextLow)}
                    >
                      {applicant.riskLevel.charAt(0).toUpperCase() + applicant.riskLevel.slice(1)}
                    </span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Distance</span>
                    <span className={styles.metricValueWhite}>{applicant.distance.toFixed(4)}</span>
                  </div>
                  <div className={styles.metricRow}>
                    <span className={styles.metricLabel}>Index</span>
                    <span className={styles.metricValueWhite}>#{applicant.index}</span>
                  </div>
                </div>

                {applicant.sources && applicant.sources.length > 0 && (
                  <div className={styles.sourceSection}>
                    <SourceBadge sources={applicant.sources} />
                  </div>
                )}

                <div className={styles.sparklineSection}>
                  <div className={styles.sparklineFull}>
                    <MiniSparkline
                      data={applicant.trendData ?? [{ value: 0.5 }, { value: applicant.similarityScore }]}
                      color={applicant.defaultLabel ? "#ef4444" : "#4ade80"}
                    />
                  </div>
                </div>
              </div>
            </ShimmerBorder>
          ))}
        </div>
        {/* Side navigation buttons - outside scroll area */}
        <button
          className={cn(styles.navButtonSide, styles.prev)}
          onClick={() => scrollByCard("prev")}
          aria-label="Previous"
        >
          <ChevronLeft className={styles.navButtonIcon} />
        </button>
        <button
          className={cn(styles.navButtonSide, styles.next)}
          onClick={() => scrollByCard("next")}
          aria-label="Next"
        >
          <ChevronRight className={styles.navButtonIcon} />
        </button>
      </div>
    </div>
  );
}
