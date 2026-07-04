"use client";

import { useState, useEffect } from "react";
import { Globe, BarChart3, Network, TriangleAlert, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { socialCapitalApi } from "@/lib/api";
import type { SocialCapitalResponse, NetworkData, ApplicantData } from "@/lib/api";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { Tabs } from "@/components/ui/tabs";
import styles from "./social-capital-panel.module.scss";

interface SocialCapitalPanelProps {
  applicantId: string;
  features: ApplicantData | null;
}

export function SocialCapitalPanel({ applicantId, features }: SocialCapitalPanelProps) {
  const [activeTab, setActiveTab] = useState<"metrics" | "network" | "risks">("metrics");
  const [data, setData] = useState<SocialCapitalResponse | null>(null);
  const [networkData, setNetworkData] = useState<NetworkData | null>(null);
  const [loading, setLoading] = useState(false);

  // Auto-fetch social capital + network visualization on features change (debounced)
  useEffect(() => {
    if (!features) return;
    let cancelled = false;
    const timeoutId = setTimeout(() => {
      async function fetchSocial() {
        if (!features) return;
        setLoading(true);
        try {
          const [score, network] = await Promise.all([
            socialCapitalApi.calculate({ entity_id: applicantId, features }),
            socialCapitalApi.getVisualizationData(applicantId, 2, features),
          ]);
          if (!cancelled) {
            setData(score);
            setNetworkData(network);
          }
        } catch {
          if (!cancelled) {
            setData(null);
            setNetworkData(null);
          }
        } finally {
          if (!cancelled) setLoading(false);
        }
      }
      fetchSocial();
    }, 300);

    return () => {
      cancelled = true;
      clearTimeout(timeoutId);
    };
  }, [applicantId, features]);

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loadingInner}>
          <Loader2 className={styles.loadingSpinner} />
          <span className={styles.loadingText}>Analyzing social capital...</span>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className={styles.emptyContainer}>
        <div className={styles.emptyInner}>
          <span className={styles.emptyIcon}><Globe className={styles.emptyIconSvg} /></span>
          <p className={styles.emptyText}>Enter applicant data to see social capital analysis</p>
        </div>
      </div>
    );
  }

  const scores = data.scores;

  return (
    <div className={styles.content}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <h2 className={styles.title}>
            <span className={styles.titleIcon}><Globe className={styles.titleIconSvg} /></span>
            Social Capital Analysis
          </h2>
          <p className={styles.subtitle}>Network-based creditworthiness assessment</p>
        </div>
        <div className={styles.headerStats}>
          <div className={styles.statCenter}>
            <p className={styles.statValue}>{data.network_size}</p>
            <p className={styles.statLabel}>Network Size</p>
          </div>
          <div className={styles.statCenter}>
            <p className={styles.statValue}>{data.connection_count}</p>
            <p className={styles.statLabel}>Connections</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs
        tabs={[
          {
            title: (<>
              <BarChart3 className={styles.tabIconSvg} />
              Metrics
            </>), value: "metrics"
          },
          {
            title: (<>
              <Network className={styles.tabIconSvg} />
              Network
            </>), value: "network"
          },
          {
            title: (<>
              <TriangleAlert className={styles.tabIconSvg} />
              Risks
            </>), value: "risks"
          },
        ]}
        activeTab={activeTab}
        onChange={(v) => setActiveTab(v as "metrics" | "network" | "risks")}
      />

      {/* Metrics Tab */}
      {activeTab === "metrics" && (
        <div className={styles.metricsContent}>
          {/* Overall Score */}
          <ShimmerBorder borderRadius="1rem">
            <div className={styles.scoreCard}>
              <div className={styles.scoreHeader}>
                <div>
                  <p className={styles.scoreLabel}>Centrality Score</p>
                  <p className={styles.scoreValue}>
                    {(scores.centrality * 100).toFixed(0)}%
                  </p>
                </div>
                <div className={styles.scoreGrid}>
                  <div className={styles.scoreSubItem}>
                    <p className={styles.scoreSubLabel}>Influence</p>
                    <p className={styles.scoreSubValue}>{(scores.influence * 100).toFixed(1)}%</p>
                  </div>
                  <div className={styles.scoreSubItem}>
                    <p className={styles.scoreSubLabel}>Trust</p>
                    <p className={styles.scoreSubValue}>{(scores.trust * 100).toFixed(1)}%</p>
                  </div>
                  <div className={styles.scoreSubItem}>
                    <p className={styles.scoreSubLabel}>Reach</p>
                    <p className={styles.scoreSubValue}>{(scores.reach * 100).toFixed(1)}%</p>
                  </div>
                  <div className={styles.scoreSubItem}>
                    <p className={styles.scoreSubLabel}>Engagement</p>
                    <p className={styles.scoreSubValue}>{(scores.engagement * 100).toFixed(1)}%</p>
                  </div>
                </div>
              </div>
            </div>
          </ShimmerBorder>

          {/* Metrics Grid */}
          <div className={styles.metricsGrid}>
            <ShimmerBorder key="centrality" borderRadius="0.75rem">
              <div className={styles.metricItem}>
                <p className={styles.metricLabel}>Centrality</p>
                <p className={styles.metricValue}>{(scores.centrality * 100).toFixed(1)}%</p>
              </div>
            </ShimmerBorder>
            <ShimmerBorder key="influence" borderRadius="0.75rem">
              <div className={styles.metricItem}>
                <p className={styles.metricLabel}>Influence</p>
                <p className={styles.metricValue}>{(scores.influence * 100).toFixed(1)}%</p>
              </div>
            </ShimmerBorder>
            <ShimmerBorder key="trust" borderRadius="0.75rem">
              <div className={styles.metricItem}>
                <p className={styles.metricLabel}>Trust</p>
                <p className={styles.metricValue}>{(scores.trust * 100).toFixed(1)}%</p>
              </div>
            </ShimmerBorder>
            <ShimmerBorder key="reach" borderRadius="0.75rem">
              <div className={styles.metricItem}>
                <p className={styles.metricLabel}>Reach</p>
                <p className={styles.metricValue}>{(scores.reach * 100).toFixed(1)}%</p>
              </div>
            </ShimmerBorder>
            <ShimmerBorder key="engagement" borderRadius="0.75rem">
              <div className={styles.metricItem}>
                <p className={styles.metricLabel}>Engagement</p>
                <p className={styles.metricValue}>{(scores.engagement * 100).toFixed(1)}%</p>
              </div>
            </ShimmerBorder>
            <ShimmerBorder key="communities" borderRadius="0.75rem">
              <div className={styles.metricItem}>
                <p className={styles.metricLabel}>Communities</p>
                <p className={styles.metricValue}>{scores.communities}</p>
              </div>
            </ShimmerBorder>
          </div>

          {/* Analysis Summary */}
          {data.analysis_summary && (
            <ShimmerBorder borderRadius="1rem">
              <div className={styles.summaryCard}>
                <h3 className={styles.summaryTitle}>Summary</h3>
                <p className={styles.summaryText}>{data.analysis_summary}</p>
              </div>
            </ShimmerBorder>
          )}
        </div>
      )}

      {/* Network Tab */}
      {activeTab === "network" && networkData && (
        <ShimmerBorder borderRadius="1rem">
          <div className={styles.networkCard}>
            <h3 className={styles.networkTitle}>Network Structure</h3>
            <div className={styles.networkStatsGrid}>
              <div className={styles.networkStatItem}>
                <p className={styles.networkStatLabel}>Nodes</p>
                <p className={styles.networkStatValue}>{networkData.total_nodes}</p>
              </div>
              <div className={styles.networkStatItem}>
                <p className={styles.networkStatLabel}>Edges</p>
                <p className={styles.networkStatValue}>{networkData.total_edges}</p>
              </div>
              <div className={styles.networkStatItem}>
                <p className={styles.networkStatLabel}>Communities</p>
                <p className={styles.networkStatValue}>{networkData.communities}</p>
              </div>
            </div>

            {/* Node Legend */}
            <div className={styles.nodeLegend}>
              {networkData.nodes.slice(0, 8).map((node) => (
                <div key={node.id} className={styles.nodeLegendItem}>
                  <span className={cn(
                    styles.nodeDot,
                    node.type === "individual" ? styles.nodeDotIndividual :
                      node.type === "organization" ? styles.nodeDotOrganization :
                        node.type === "business" ? styles.nodeDotBusiness :
                          styles.nodeDotOther
                  )} />
                  <span className={styles.nodeLabel}>{node.label}</span>
                </div>
              ))}
              {networkData.nodes.length > 8 && (
                <span className={styles.moreNodes}>+{networkData.nodes.length - 8} more</span>
              )}
            </div>
          </div>
        </ShimmerBorder>
      )}

      {activeTab === "network" && !networkData && (
        <div className={styles.noDataContainer}>
          <p className={styles.noDataText}>No network data available</p>
        </div>
      )}

      {/* Risks Tab */}
      {activeTab === "risks" && data.risk_indicators && (
        <div className={styles.risksContent}>
          {Object.entries(data.risk_indicators).map(([key, value]) => {
            const numVal = typeof value === "number" ? value : parseFloat(String(value)) || 0;
            // Caps match the social capital service output ranges (services/social_capital/app/main.py):
            // fraud ≤ 0.95, default ≤ 0.9, reputational ≤ 0.85, anomaly ≤ 0.4
            const maxMap: Record<string, number> = {
              fraud_risk: 0.95,
              default_risk: 0.9,
              reputational_risk: 0.85,
              anomaly_score: 0.4,
            };
            const max = maxMap[key] ?? 1;
            const normalized = Math.min(1, numVal / max);
            const level = normalized < 0.33 ? "low" : normalized < 0.66 ? "medium" : "high";
            return (
              <ShimmerBorder key={key} borderRadius="0.75rem">
                <div className={styles.riskItem}>
                  <div className={styles.riskInfo}>
                    <p className={styles.riskName}>
                      {key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}
                    </p>
                    <p className={styles.riskLevel}>
                      {level === "low" ? "Low risk" : level === "medium" ? "Moderate risk" : "High risk"}
                    </p>
                  </div>
                  <div className={styles.riskBarSection}>
                    <div className={styles.riskBarTrack}>
                      <div
                        className={cn(
                          styles.riskBarFill,
                          level === "low" ? styles.riskBarFillLow :
                            level === "medium" ? styles.riskBarFillMedium :
                              styles.riskBarFillHigh
                        )}
                        style={{ width: `${normalized * 100}%` }}
                      />
                    </div>
                    <span className={cn(
                      styles.riskValue,
                      level === "low" ? styles.riskValueLow :
                        level === "medium" ? styles.riskValueMedium :
                          styles.riskValueHigh
                    )}>
                      {(normalized * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </ShimmerBorder>
            );
          })}
        </div>
      )}

      {activeTab === "risks" && !data.risk_indicators && (
        <div className={styles.noDataContainer}>
          <p className={styles.noDataText}>No risk indicators available</p>
        </div>
      )}
    </div>
  );
}
