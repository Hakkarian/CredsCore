"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { cn } from "@/lib/utils";
import { usePeerGroupsMutation, useGenerateSyntheticData } from "@/hooks/use-credit-api";
import { PeerGroupsResult, SyntheticDataResponse, ApplicantData } from "@/lib/api";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./groups-panel.module.scss";

interface GroupsPanelProps {
  onDataGenerated?: (data: SyntheticDataResponse) => void;
}

export function GroupsPanel({ onDataGenerated }: GroupsPanelProps = {}) {
  const [result, setResult] = useState<PeerGroupsResult | null>(null);
  const [nClusters, setNClusters] = useState(5);
  const [uploadedData, setUploadedData] = useState<ApplicantData[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);
  const [generatedData, setGeneratedData] = useState<SyntheticDataResponse | null>(null);

  const { mutate: analyzeGroups, isPending } = usePeerGroupsMutation();
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

  const handleAnalyze = () => {
    const data = uploadedData.length > 0 ? uploadedData : [];
    analyzeGroups(
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

  const segmentRiskStyles: Record<string, string> = {
    high: styles.segmentRiskHigh,
    medium: styles.segmentRiskMedium,
    low: styles.segmentRiskLow,
  };

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
                Number of Segments
              </label>
              <input
                type="number"
                min={2}
                max={20}
                value={nClusters}
                onChange={(e) => setNClusters(parseInt(e.target.value) || 5)}
                className={styles.numberInput}
              />
            </div>
          </div>

          <div className={styles.buttonRow}>
            <button
              onClick={handleAnalyze}
              disabled={isPending}
              className={cn(
                styles.primaryButton,
                isPending && styles.primaryButtonDisabled
              )}
            >
              {isPending ? "Analyzing..." : "Analyze Peer Groups"}
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
      )}

      {/* Generated Data Info */}
      {generatedData && (
        <ShimmerBorder borderRadius="1rem">
          <div>
            <h3 className={styles.sectionTitleMb2}>Generated Synthetic Data</h3>
            <p className={styles.dropzoneFileCount}>
              {generatedData.num_records || generatedData.records?.length || 0} records generated
            </p>
            {generatedData.quality_metrics && (
              <div className={styles.qualityGrid}>
                {Object.entries(generatedData.quality_metrics).slice(0, 4).map(([key, value]) => (
                  <div key={key} className={styles.qualityCard}>
                    <p className={styles.qualityLabel}>{key.replace(/_/g, " ")}</p>
                    <p className={styles.qualityValue}>
                      {typeof value === "number" ? (value * 100).toFixed(1) + "%" : String(value)}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </ShimmerBorder>
      )}
    </div>
  );
}
