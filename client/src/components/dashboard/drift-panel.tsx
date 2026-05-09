"use client";

import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { cn } from "@/lib/utils";
import { useDriftMonitorMutation, useGenerateSyntheticData } from "@/hooks/use-credit-api";
import { DriftResult, SyntheticDataResponse, ApplicantData } from "@/lib/api";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./drift-panel.module.scss";

interface DriftPanelProps {
  onDataGenerated?: (data: SyntheticDataResponse) => void;
}

export function DriftPanel({ onDataGenerated }: DriftPanelProps = {}) {
  const [result, setResult] = useState<DriftResult | null>(null);
  const [nClusters, setNClusters] = useState(10);
  const [uploadedData, setUploadedData] = useState<ApplicantData[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);
  const [generatedData, setGeneratedData] = useState<SyntheticDataResponse | null>(null);

  const { mutate: monitorDrift, isPending } = useDriftMonitorMutation();
  const generateMutation = useGenerateSyntheticData();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = e => {
        try {
          let text = e.target?.result as string;
          if (text.charCodeAt(0) === 0xFEFF) {
            text = text.substring(1);
          }

          let data: ApplicantData[] = [];

          try {
            const parsed = JSON.parse(text.trim());
            let rawData: any[] = [];

            if (Array.isArray(parsed)) {
              rawData = parsed;
            } else if (parsed && typeof parsed === 'object') {
              if (Array.isArray(parsed.records)) {
                rawData = parsed.records;
              } else if (Array.isArray(parsed.data)) {
                rawData = parsed.data;
              } else {
                rawData = [parsed];
              }
            }

            data = rawData.filter(item => item && typeof item === 'object');
          } catch {
            const lines = text.trim().split('\n');
            if (lines.length > 1) {
              const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
              data = lines.slice(1).map(line => {
                const values = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''));
                const record: any = {};
                headers.forEach((header, idx) => {
                  const value = values[idx];
                  record[header] = isNaN(Number(value)) ? value : Number(value);
                });
                return record;
              }).filter(record => Object.keys(record).length > 0);
            }
          }

          if (data.length > 0) {
            setUploadedData(data);
          } else {
            alert("No valid data found in file. Please use JSON or CSV format.");
          }
        } catch (err) {
          alert("Error parsing file: " + (err instanceof Error ? err.message : "Unknown error"));
        }
      };
      reader.readAsText(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'text/csv': ['.csv'],
    },
    multiple: false,
  });

  const handleMonitor = () => {
    const data = uploadedData.length > 0 ? uploadedData : [];
    monitorDrift(
      { nClusters, data },
      {
        onSuccess: (data) => setResult(data),
      }
    );
  };

  const handleGenerateSynthetic = () => {
    generateMutation.mutate(
      { num_records: 500, apply_constraints: true, random_seed: null },
      {
        onSuccess: (data) => {
          setGeneratedData(data);
          onDataGenerated?.(data);
        },
      }
    );
  };

  function getDriftColorClass(level: string | undefined): string {
    if (!level) return styles.driftTextNeutral;
    const l = level.toLowerCase();
    if (l.includes("high")) return styles.driftTextHigh;
    if (l.includes("medium")) return styles.driftTextMedium;
    return styles.driftTextLow;
  }

  function getDriftBgClass(level: string | undefined): string {
    if (!level) return styles.driftBadgeDefault;
    const l = level.toLowerCase();
    if (l.includes("high")) return styles.driftBadgeHigh;
    if (l.includes("medium")) return styles.driftBadgeMedium;
    return styles.driftBadgeLow;
  }

  return (
    <div className={styles.container}>
      {/* Upload Area */}
      <ShimmerBorder borderRadius="1rem">
        <div>
          <h3 className={styles.uploadHeading}>
            <span className={styles.uploadIcon}>&#x1F4C1;</span>
            Upload Data
          </h3>
          <div
            {...getRootProps()}
            className={cn(
              styles.dropzone,
              isDragActive && styles.dropzoneActive
            )}
          >
            <input {...getInputProps()} />
            {fileName ? (
              <div className={styles.dropzoneContent}>
                <p className={styles.dropzoneFileName}>{fileName}</p>
                <p className={styles.dropzoneFileCount}>{uploadedData.length} records loaded</p>
              </div>
            ) : (
              <div className={styles.dropzoneContent}>
                <p className={styles.dropzonePlaceholder}>Drop a JSON or CSV file here</p>
                <p className={styles.dropzoneHint}>or click to browse</p>
              </div>
            )}
          </div>
        </div>
      </ShimmerBorder>

      {/* Controls */}
      <ShimmerBorder borderRadius="1rem">
        <div className={styles.controlsSection}>
          <div className={styles.controlsRow}>
            <div className={styles.controlField}>
              <label className={styles.controlLabel}>
                Number of Clusters
              </label>
              <input
                type="number"
                min={2}
                max={20}
                value={nClusters}
                onChange={(e) => setNClusters(parseInt(e.target.value) || 10)}
                className={styles.numberInput}
              />
            </div>
          </div>

          <div className={styles.buttonRow}>
            <button
              onClick={handleMonitor}
              disabled={isPending}
              className={cn(
                styles.primaryButton,
                isPending && styles.primaryButtonDisabled
              )}
            >
              {isPending ? "Monitoring..." : "Monitor Drift"}
            </button>
            <button
              onClick={handleGenerateSynthetic}
              disabled={generateMutation.isPending}
              className={cn(
                styles.secondaryButton,
                generateMutation.isPending && styles.secondaryButtonDisabled
              )}
            >
              {generateMutation.isPending ? "Generating..." : "Generate Synthetic Data"}
            </button>
          </div>
        </div>
      </ShimmerBorder>

      {/* Results */}
      {result && (
        <ShimmerBorder borderRadius="1rem">
          <div className={styles.controlsSection}>
            <div className={styles.driftResultHeader}>
              <h3 className={styles.sectionTitle}>Drift Monitoring Results</h3>
              <div className={cn(styles.driftBadge, getDriftBgClass(result.drift_analysis.drift_level))}>
                <span className={cn(styles.driftBadgeText, getDriftColorClass(result.drift_analysis.drift_level))}>
                  {result.drift_analysis.drift_level}
                </span>
              </div>
            </div>

            {/* Summary Stats from drift_analysis */}
            <div className={styles.driftSummaryGrid}>
              <div className={styles.driftSummaryCard}>
                <p className={styles.driftSummaryLabel}>KL Divergence</p>
                <p className={styles.driftSummaryValue}>
                  {result.drift_analysis.kl_divergence.toFixed(3)}
                </p>
              </div>
              <div className={styles.driftSummaryCard}>
                <p className={styles.driftSummaryLabel}>Avg Distance</p>
                <p className={styles.driftSummaryValue}>
                  {result.drift_analysis.avg_centroid_distance.toFixed(3)}
                </p>
              </div>
              <div className={styles.driftSummaryCard}>
                <p className={styles.driftSummaryLabel}>Max Distance</p>
                <p className={styles.driftSummaryValue}>
                  {result.drift_analysis.max_centroid_distance.toFixed(3)}
                </p>
              </div>
              <div className={styles.driftSummaryCard}>
                <p className={styles.driftSummaryLabel}>Detected</p>
                <p className={cn(
                  result.drift_analysis.drift_detected ? styles.driftSummaryValueRed : styles.driftSummaryValueGreen
                )}>
                  {result.drift_analysis.drift_detected ? "Yes" : "No"}
                </p>
              </div>
            </div>

            {/* Interpretation */}
            {result.interpretation && (
              <div className={styles.interpretationSection}>
                <h4 className={styles.interpretationSectionTitle}>Interpretation</h4>
                <div className={styles.interpretationCard}>
                  {result.interpretation.drift_detected !== undefined && (
                    <div className={styles.interpretationRow}>
                      <span className={styles.interpretationLabel}>Drift Detected</span>
                      <span className={result.interpretation.drift_detected ? styles.interpretationValueRed : styles.interpretationValueGreen}>
                        {result.interpretation.drift_detected ? "Yes" : "No"}
                      </span>
                    </div>
                  )}
                  {result.interpretation.drift_level && (
                    <div className={styles.interpretationRow}>
                      <span className={styles.interpretationLabel}>Drift Level</span>
                      <span className={cn(
                        styles.interpretationValue,
                        getDriftColorClass(result.interpretation.drift_level)
                      )}>
                        {result.interpretation.drift_level}
                      </span>
                    </div>
                  )}
                  {result.interpretation.kl_divergence && (
                    <div className={styles.interpretationRow}>
                      <span className={styles.interpretationLabel}>KL Divergence</span>
                      <span className={styles.interpretationValue}>{result.interpretation.kl_divergence}</span>
                    </div>
                  )}
                  {result.interpretation.avg_centroid_shift && (
                    <div className={styles.interpretationRow}>
                      <span className={styles.interpretationLabel}>Avg Centroid Shift</span>
                      <span className={styles.interpretationValue}>{result.interpretation.avg_centroid_shift}</span>
                    </div>
                  )}
                  {result.interpretation.recommendation && (
                    <div className={styles.recommendation}>
                      <p className={styles.recommendationLabel}>Recommendation</p>
                      <p className={styles.recommendationText}>{result.interpretation.recommendation}</p>
                    </div>
                  )}
                </div>
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
      )}

      {/* Generated Data Info */}
      {generatedData && (
        <ShimmerBorder borderRadius="1rem">
          <div>
            <h3 className={styles.sectionTitleMb2}>Generated Synthetic Data</h3>
            <p className={styles.generatedDataInfo}>
              {generatedData.num_records || generatedData.records?.length || 0} records generated
            </p>
          </div>
        </ShimmerBorder>
      )}
    </div>
  );
}
