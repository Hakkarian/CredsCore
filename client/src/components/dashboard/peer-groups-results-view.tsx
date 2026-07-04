"use client";

import { cn } from "@/lib/utils";
import { PeerGroupsResult } from "@/lib/api";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./groups-panel.module.scss";

interface PeerGroupsResultsViewProps {
  result: PeerGroupsResult;
}

const segmentRiskStyles: Record<string, string> = {
  high: styles.segmentRiskHigh,
  medium: styles.segmentRiskMedium,
  low: styles.segmentRiskLow,
};

export function PeerGroupsResultsView({ result }: PeerGroupsResultsViewProps) {
  return (
    <ShimmerBorder borderRadius="1rem">
      <div className={styles.controlsSection}>
        <h3 className={styles.sectionTitle}>Peer Group Results</h3>

        {/* Summary Stats */}
        <div className={styles.summaryGrid}>
          <div className={styles.summaryCard}>
            <p className={styles.summaryLabel}>Segments</p>
            <p className={styles.summaryValuePrimary}>{result.n_segments}</p>
          </div>
          <div className={styles.summaryCard}>
            <p className={styles.summaryLabel}>Customers</p>
            <p className={styles.summaryValueNeutral}>{result.total_customers}</p>
          </div>
          <div className={styles.summaryCard}>
            <p className={styles.summaryLabel}>Highest Risk</p>
            <p className={styles.summaryValueRisk}>{result.summary.highest_risk_segment || "-"}</p>
          </div>
        </div>

        {/* Segment Details */}
        {result.segments && result.segments.length > 0 && (
          <div className={styles.segmentSection}>
            <h4 className={styles.segmentSectionTitle}>Segment Details</h4>
            {result.segments.map((segment, i) => (
              <div key={i} className={styles.segmentCard}>
                <div className={styles.segmentHeader}>
                  <span className={styles.segmentName}>{segment.segment}</span>
                  <div className={styles.segmentBadges}>
                    <span className={styles.segmentBadge}>
                      {segment.size} members ({segment.percentage})
                    </span>
                    <span className={cn(styles.segmentRiskBadge, segmentRiskStyles[segment.risk_level] ?? styles.segmentRiskLow)}>
                      {segment.risk_level}
                    </span>
                  </div>
                </div>
                <div className={styles.segmentMeta}>
                  <span className={styles.segmentMetaLabel}>Default rate:</span>
                  <span className={styles.segmentMetaValue}>{segment.default_rate}</span>
                </div>
                {segment.profile && Object.keys(segment.profile).length > 0 && (
                  <div className={styles.segmentProfileGrid}>
                    {Object.entries(segment.profile).slice(0, 6).map(([key, value]) => (
                      <div key={key} className={styles.segmentProfileRow}>
                        <span className={styles.segmentProfileKey}>{key}</span>
                        <span className={styles.segmentProfileValue}>
                          {typeof value === "number" ? value.toFixed(2) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Human Explanation */}
        {result.human_explanation && (
          <div className={styles.explanationBox}>
            <p className={styles.explanationText}>{result.human_explanation}</p>
          </div>
        )}
      </div>
    </ShimmerBorder>
  );
}