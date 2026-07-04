"use client";

import { useState, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";
import { Palette } from "lucide-react";
import { syntheticDataApi, SyntheticDataResponse, SyntheticAnalysisResponse, QualityMetrics, SyntheticRecord } from "@/lib/api";
import { ShimmerBorder, ShimmerTiltCard } from "@/components/ui/shimmer-tilt-card";
import { DriftResultsView } from "@/components/dashboard/drift-results-view";
import { PeerGroupsResultsView } from "@/components/dashboard/peer-groups-results-view";
import { GanModelStatus } from "./gan-model-status";
import { QualityMetricsDisplay } from "./quality-metrics";
import { DataPreview } from "./data-preview";
import styles from "./gan-panel.module.scss";

interface GanPanelProps {
  onGenerate?: (data: SyntheticDataResponse) => void;
}

export function GanPanel({ onGenerate }: GanPanelProps) {
  const [numRecords, setNumRecords] = useState(500);
  const [applyConstraints, setApplyConstraints] = useState(true);
  const [randomSeed, setRandomSeed] = useState<string>("");
  const [generatedData, setGeneratedData] = useState<SyntheticAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleGenerate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const seed = randomSeed ? parseInt(randomSeed) : null;
      const result = await syntheticDataApi.generateSyntheticDataWithAnalysis({
        num_records: numRecords,
        apply_constraints: applyConstraints,
        random_seed: seed,
        drift_n_clusters: 10,
        peer_n_clusters: 5,
      });
      setGeneratedData(result);
      onGenerate?.(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate data");
    } finally {
      setLoading(false);
    }
  }, [numRecords, applyConstraints, randomSeed, onGenerate]);

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <h2 className={styles.title}>
          <Palette className={styles.titleIcon} size={22} />
          Synthetic Data Generator
        </h2>
        <p className={styles.subtitle}>Generate realistic synthetic credit data with GAN</p>
      </div>

      {/* Model Status */}
      <GanModelStatus />

      {/* Generation Controls */}
      <ShimmerBorder borderRadius="1rem">
        <div className={styles.controlsSection}>
          <div className={styles.controlsGrid}>
            <div>
              <label className={styles.fieldLabel}>
                Number of Records
              </label>
              <input
                type="number"
                min={1}
                max={100000}
                value={numRecords}
                onChange={(e) => setNumRecords(parseInt(e.target.value) || 500)}
                className={styles.input}
              />
            </div>
            <div>
              <label className={styles.fieldLabel}>
                Random Seed
              </label>
              <input
                type="text"
                value={randomSeed}
                onChange={(e) => setRandomSeed(e.target.value)}
                placeholder="Optional"
                className={styles.input}
              />
            </div>
          </div>

          <div className={styles.toggleRow}>
            <button
              type="button"
              role="switch"
              aria-checked={applyConstraints}
              onClick={() => setApplyConstraints(!applyConstraints)}
              className={cn(
                applyConstraints ? styles.toggleTrackActive : styles.toggleTrack
              )}
            >
              <span
                className={cn(
                  applyConstraints ? styles.toggleThumbActive : styles.toggleThumb
                )}
              />
            </button>
            <span className={styles.toggleLabel}>Apply domain constraints</span>
          </div>

          {/* Advanced Settings */}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={styles.advancedToggle}
          >
            {showAdvanced ? "Hide" : "Show"} advanced settings
          </button>

          {showAdvanced && (
            <div className={styles.advancedPanel}>
              <p className={styles.advancedDescription}>
                Advanced GAN configuration options. These affect the generation quality and speed.
              </p>
              <div className={styles.advancedGrid}>
                <div>
                  <label className={styles.advancedFieldLabel}>Noise Dimension</label>
                  <input
                    type="number"
                    defaultValue={100}
                    className={styles.advancedInput}
                  />
                </div>
                <div>
                  <label className={styles.advancedFieldLabel}>Epochs</label>
                  <input
                    type="number"
                    defaultValue={200}
                    className={styles.advancedInput}
                  />
                </div>
              </div>
            </div>
          )}

          <button
            onClick={handleGenerate}
            disabled={loading}
            className={cn(
              loading ? styles.generateButtonDisabled : styles.generateButton
            )}
          >
            {loading ? (
              <span className={styles.generateButtonInner}>
                <svg className={styles.spinner} viewBox="0 0 24 24" fill="none">
                  <circle className={styles.spinnerCircle} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className={styles.spinnerPath} fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Generating...
              </span>
            ) : (
              "Generate Synthetic Data"
            )}
          </button>
        </div>
      </ShimmerBorder>

      {/* Error */}
      {error && (
        <div className={styles.errorContainer}>
          <p className={styles.errorText}>{error}</p>
        </div>
      )}

      {/* Quality Metrics */}
      {generatedData?.quality_metrics && (
        <QualityMetricsDisplay metrics={generatedData.quality_metrics} />
      )}

      {/* Data Preview */}
      {generatedData?.records && generatedData.records.length > 0 && (
        <DataPreview records={generatedData.records} totalCount={generatedData.num_records || generatedData.records.length} />
      )}

      {/* Generation Summary */}
      {generatedData && !error && (
        <ShimmerBorder borderRadius="1rem">
          <div className={styles.summarySection}>
            <h3 className={styles.summaryTitle}>Generation Summary</h3>
            <div className={styles.summaryGrid}>
              <div className={styles.summaryCenter}>
                <p className={styles.summaryLabel}>Records</p>
                <p className={styles.summaryValuePrimary}>{generatedData.num_records || generatedData.records?.length || 0}</p>
              </div>
              <div className={styles.summaryCenter}>
                <p className={styles.summaryLabel}>Seed</p>
                <p className={styles.summaryValue}>{randomSeed || "Random"}</p>
              </div>
              <div className={styles.summaryCenter}>
                <p className={styles.summaryLabel}>Constrained</p>
                <p className={styles.summaryValue}>{applyConstraints ? "Yes" : "No"}</p>
              </div>
            </div>
          </div>
        </ShimmerBorder>
      )}

      {/* Drift Analysis (auto-computed on generation) */}
      {generatedData && (generatedData.drift || generatedData.drift_error) && (
        <div>
          <h3 className={styles.analysisSectionTitle}>Drift Analysis</h3>
          {generatedData.drift ? (
            <DriftResultsView result={generatedData.drift} />
          ) : (
            <div className={styles.errorContainer}>
              <p className={styles.errorText}>{generatedData.drift_error}</p>
            </div>
          )}
        </div>
      )}

      {/* Peer Groups (auto-computed on generation) */}
      {generatedData && (generatedData.peer_groups || generatedData.peer_groups_error) && (
        <div>
          <h3 className={styles.analysisSectionTitle}>Peer Groups</h3>
          {generatedData.peer_groups ? (
            <PeerGroupsResultsView result={generatedData.peer_groups} />
          ) : (
            <div className={styles.errorContainer}>
              <p className={styles.errorText}>{generatedData.peer_groups_error}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
