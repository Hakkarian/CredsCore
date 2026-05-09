"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { socialCapitalApi, SocialCapitalResponse, NetworkData } from "@/lib/api";
import { ShimmerTiltCard } from "@/components/ui/shimmer-tilt-card";
import { NetworkGraph } from "./NetworkGraph";
import { RiskIndicators } from "./RiskIndicators";
import styles from "./SocialCapitalPanel.module.scss";

interface SocialCapitalPanelProps {
  applicantId: string;
}

export function SocialCapitalPanel({ applicantId }: SocialCapitalPanelProps) {
  const [socialData, setSocialData] = useState<SocialCapitalResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!applicantId) return;

    async function fetchSocialData() {
      setLoading(true);
      setError(null);
      try {
        const result = await socialCapitalApi.calculate({
          entity_id: applicantId,
          entity_type: "individual",
          depth: 2,
        });
        setSocialData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load social data");
      } finally {
        setLoading(false);
      }
    }

    fetchSocialData();
  }, [applicantId]);

  if (loading) {
    return (
      <div className={styles.stateContainer}>
        <div className={styles.loadingInner}>
          <svg className={styles.loadingSpinner} viewBox="0 0 24 24" fill="none">
            <circle className={styles.spinnerCircle} cx="12" cy="12" r="10" stroke="#F3CA40" strokeWidth="4" />
            <path className={styles.spinnerPath} fill="#F3CA40" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.stateContainer}>
        <div className={styles.errorInner}>
          <p className={styles.errorText}>{error}</p>
          <button className={styles.retryButton} onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!socialData) {
    return (
      <div className={styles.stateContainer}>
        <div className={styles.emptyInner}>
          <span className={styles.emptyIcon}>&#x1F310;</span>
          <p className={styles.emptyText}>No social capital data available</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: "metrics", label: "Metrics", icon: "&#x1F4CA;" },
    { id: "network", label: "Network", icon: "&#x1F517;" },
    { id: "risks", label: "Risks", icon: "&#x26A0;" },
  ] as const;

  type TabId = (typeof tabs)[number]["id"];
  const [activeTab, setActiveTab] = useState<TabId>("metrics");

  return (
    <div className={styles.content}>
      <div className={styles.headerCard}>
        <div className={styles.headerInner}>
          <div>
            <h3 className={styles.headerTitle}>
              <span className={styles.headerTitleIcon}>&#x1F310;</span>
              Social Capital Analysis
            </h3>
            <p className={styles.headerSubtitle}>Network-based creditworthiness assessment</p>
          </div>
          <div className={styles.headerRight}>
            <p className={styles.centralityLabel}>Centrality</p>
            <p className={styles.centralityValue}>
              {socialData.scores ? (socialData.scores.centrality * 100).toFixed(0) : 0}%
            </p>
          </div>
        </div>
      </div>

      <div className={styles.metricsGrid}>
        <div className={styles.metricItem}>
          <p className={styles.metricLabel}>Network Size</p>
          <p className={cn(styles.metricValue, styles.metricValuePrimary)}>{socialData.network_size}</p>
        </div>
        <div className={styles.metricItem}>
          <p className={styles.metricLabel}>Connections</p>
          <p className={cn(styles.metricValue, styles.metricValuePrimary)}>{socialData.connection_count}</p>
        </div>
        <div className={styles.metricItem}>
          <p className={styles.metricLabel}>Communities</p>
          <p className={cn(styles.metricValue, styles.metricValuePrimary)}>{socialData.scores?.communities ?? 0}</p>
        </div>
      </div>

      {activeTab === "network" && (
        <div className={styles.networkSection}>
          <div className={styles.networkSectionInner}>
            <h4 className={styles.networkTitle}>Network Visualization</h4>
            <NetworkGraph applicantId={applicantId} />
          </div>
        </div>
      )}

      {activeTab === "risks" && socialData.risk_indicators && (
        <RiskIndicators indicators={socialData.risk_indicators} />
      )}
    </div>
  );
}
