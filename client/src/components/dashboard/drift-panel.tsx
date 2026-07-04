"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { FolderOpen } from "lucide-react";
import { cn } from "@/lib/utils";
import { useDriftMonitorMutation } from "@/hooks/use-credit-api";
import { DriftResult, ApplicantData } from "@/lib/api";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { DriftResultsView } from "./drift-results-view";
import styles from "./drift-panel.module.scss";

export function DriftPanel() {
  const [result, setResult] = useState<DriftResult | null>(null);
  const [nClusters, setNClusters] = useState(10);
  const [uploadedData, setUploadedData] = useState<ApplicantData[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);

  const { mutate: monitorDrift, isPending } = useDriftMonitorMutation();

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

  return (
    <div className={styles.container}>
      {/* Upload Area */}
      <ShimmerBorder borderRadius="1rem">
        <div>
          <h3 className={styles.uploadHeading}>
            <span className={styles.uploadIcon}><FolderOpen className={styles.uploadIconSvg} /></span>
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
          </div>
        </div>
      </ShimmerBorder>

      {/* Results */}
      {result && <DriftResultsView result={result} />}
    </div>
  );
}