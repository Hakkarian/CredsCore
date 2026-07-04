"use client";

import { useState, useCallback, useRef } from "react";
import { cn } from "@/lib/utils";
import { FlaskConical } from "lucide-react";
import { syntheticDataApi, SyntheticDataResponse, QualityMetrics } from "@/lib/api";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { QualityMetricsDisplay } from "./quality-metrics";
import { DataPreview } from "./data-preview";
import styles from "./test-panel.module.scss";

interface TestPanelProps {
  onGenerate?: (data: SyntheticDataResponse) => void;
}

export function TestPanel({ onGenerate }: TestPanelProps = {}) {
  const [numRecords, setNumRecords] = useState(500);
  const [applyConstraints, setApplyConstraints] = useState(true);
  const [randomSeed, setRandomSeed] = useState<string>("");
  const [generatedData, setGeneratedData] = useState<SyntheticDataResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<{ name: string; passed: boolean; details: string }[]>([]);

  const handleGenerate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const seed = randomSeed ? parseInt(randomSeed) : null;
      const result = await syntheticDataApi.generateSyntheticData({
        num_records: numRecords,
        apply_constraints: applyConstraints,
        random_seed: seed,
      });
      setGeneratedData(result);
      onGenerate?.(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate data");
    } finally {
      setLoading(false);
    }
  }, [numRecords, applyConstraints, randomSeed, onGenerate]);

  const handleRunTests = useCallback(async () => {
    if (!generatedData) return;

    const results: { name: string; passed: boolean; details: string }[] = [];

    // Test 1: Check record count
    const recordCount = generatedData.records?.length || generatedData.num_records || 0;
    results.push({
      name: "Record Count",
      passed: recordCount >= numRecords * 0.9,
      details: `Generated ${recordCount} records (expected ~${numRecords})`,
    });

    // Test 2: Check feature completeness
    if (generatedData.records && generatedData.records.length > 0) {
      const firstRecord = generatedData.records[0];
      const expectedFeatures = [
        "RevolvingUtilizationOfUnsecuredLines",
        "age",
        "DebtRatio",
        "MonthlyIncome",
        "NumberOfTime30_59DaysPastDueNotWorse",
        "NumberOfOpenCreditLinesAndLoans",
        "NumberOfTimes90DaysLate",
        "NumberRealEstateLoansOrLines",
        "NumberOfTime60_89DaysPastDueNotWorse",
        "NumberOfDependents",
      ];
      const presentFeatures = expectedFeatures.filter(f => f in firstRecord);
      results.push({
        name: "Feature Completeness",
        passed: presentFeatures.length >= expectedFeatures.length * 0.8,
        details: `${presentFeatures.length}/${expectedFeatures.length} features present`,
      });

      // Test 3: Check value ranges
      const ageValues = generatedData.records.map(r => r.age).filter(v => v !== undefined && v !== null);
      const validAges = ageValues.filter(a => typeof a === "number" && a >= 18 && a <= 120);
      results.push({
        name: "Value Ranges",
        passed: validAges.length >= ageValues.length * 0.95,
        details: `${validAges.length}/${ageValues.length} records have valid age range (18-120)`,
      });

      // Test 4: Check for null values
      const nullCounts = generatedData.records.map(r =>
        Object.values(r).filter(v => v === null || v === undefined).length
      );
      const totalNulls = nullCounts.reduce((sum, c) => sum + c, 0);
      results.push({
        name: "Null Check",
        passed: totalNulls === 0,
        details: totalNulls === 0 ? "No null values found" : `${totalNulls} null values found`,
      });

      // Test 5: Check distribution diversity
      const uniqueAges = new Set(ageValues).size;
      results.push({
        name: "Distribution Diversity",
        passed: uniqueAges >= 10,
        details: `${uniqueAges} unique age values`,
      });
    }

    // Test 6: Quality metrics
    if (generatedData.quality_metrics) {
      const qm = generatedData.quality_metrics;
      const statSim = qm.similarity_score ?? qm.overall_score ?? 0;
      results.push({
        name: "Quality Metrics",
        passed: statSim >= 0.7,
        details: `Statistical similarity: ${(statSim * 100).toFixed(1)}%`,
      });
    }

    setTestResults(results);
  }, [generatedData, numRecords]);

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <h2 className={styles.title}>
          <FlaskConical className={styles.titleIcon} size={22} />
          Synthetic Data Test Panel
        </h2>
        <p className={styles.subtitle}>Generate and validate synthetic credit data</p>
      </div>

      {/* Controls */}
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

          <div className={styles.buttonRow}>
            <button
              onClick={handleGenerate}
              disabled={loading}
              className={cn(
                loading ? styles.generateButtonDisabled : styles.generateButton
              )}
            >
              {loading ? "Generating..." : "Generate Data"}
            </button>
            <button
              onClick={handleRunTests}
              disabled={!generatedData}
              className={cn(
                !generatedData ? styles.testButtonDisabled : styles.testButton
              )}
            >
              Run Validation Tests
            </button>
          </div>
        </div>
      </ShimmerBorder>

      {/* Error */}
      {error && (
        <div className={styles.errorContainer}>
          <p className={styles.errorText}>{error}</p>
        </div>
      )}

      {/* Test Results */}
      {testResults.length > 0 && (
        <ShimmerBorder borderRadius="1rem">
          <div className={styles.resultsSection}>
            <h3 className={styles.resultsTitle}>Validation Results</h3>
            <div className={styles.resultsList}>
              {testResults.map((result, i) => (
                <div
                  key={i}
                  className={cn(
                    result.passed ? styles.resultRowPass : styles.resultRowFail
                  )}
                >
                  <span className={cn(
                    result.passed ? styles.resultBadgePass : styles.resultBadgeFail
                  )}>
                    {result.passed ? "\u2713" : "\u2717"}
                  </span>
                  <div className={styles.resultContent}>
                    <p className={styles.resultName}>{result.name}</p>
                    <p className={styles.resultDetails}>{result.details}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className={styles.overallRow}>
              <span className={styles.overallLabel}>Overall</span>
              <span className={cn(
                testResults.every(r => r.passed) ? styles.overallAllPass : styles.overallPartial
              )}>
                {testResults.filter(r => r.passed).length}/{testResults.length} passed
              </span>
            </div>
          </div>
        </ShimmerBorder>
      )}

      {/* Quality Metrics */}
      {generatedData?.quality_metrics && (
        <QualityMetricsDisplay metrics={generatedData.quality_metrics} />
      )}

      {/* Data Preview */}
      {generatedData?.records && generatedData.records.length > 0 && (
        <DataPreview records={generatedData.records} totalCount={generatedData.num_records || generatedData.records.length} />
      )}
    </div>
  );
}
