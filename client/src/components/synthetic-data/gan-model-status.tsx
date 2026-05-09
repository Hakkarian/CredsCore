"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./gan-model-status.module.scss";

interface ModelStatus {
  status: "idle" | "training" | "ready" | "error";
  epoch?: number;
  total_epochs?: number;
  loss?: number;
  accuracy?: number;
  last_trained?: string;
}

export function GanModelStatus() {
  const [status, setStatus] = useState<ModelStatus>({ status: "idle" });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check model status from the synthetic data service
    async function checkStatus() {
      try {
        const response = await fetch("http://localhost:8007/model-status");
        if (response.ok) {
          const data = await response.json();
          setStatus({
            status: data.status || "ready",
            epoch: data.epoch,
            total_epochs: data.total_epochs,
            loss: data.loss,
            accuracy: data.accuracy,
            last_trained: data.last_trained,
          });
        } else {
          setStatus({ status: "idle" });
        }
      } catch {
        setStatus({ status: "idle" });
      } finally {
        setLoading(false);
      }
    }

    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  function getStatusDotClass(s: string): string {
    switch (s) {
      case "ready":
        return styles.statusDotReady;
      case "training":
        return styles.statusDotTraining;
      case "error":
        return styles.statusDotError;
      default:
        return styles.statusDotIdle;
    }
  }

  function getStatusBadgeClass(s: string): string {
    switch (s) {
      case "ready":
        return styles.statusBadgeReady;
      case "training":
        return styles.statusBadgeTraining;
      case "error":
        return styles.statusBadgeError;
      default:
        return styles.statusBadgeIdle;
    }
  }

  function getStatusTextClass(s: string): string {
    switch (s) {
      case "ready":
        return styles.statusTextReady;
      case "training":
        return styles.statusTextTraining;
      case "error":
        return styles.statusTextError;
      default:
        return styles.statusTextIdle;
    }
  }

  return (
    <ShimmerBorder borderRadius="1rem">
      <div className={styles.container}>
        <div className={styles.headerRow}>
          <div className={styles.statusInfo}>
            <span className={cn(styles.statusDot, getStatusDotClass(status.status))} />
            <div className={styles.statusText}>
              <h3 className={styles.modelName}>GAN Model</h3>
              <p className={styles.modelSubtext}>
                {status.status === "training"
                  ? `Training epoch ${status.epoch || 0}/${status.total_epochs || "?"}`
                  : status.last_trained
                  ? `Last trained: ${status.last_trained}`
                  : "Status check pending"}
              </p>
            </div>
          </div>
          <div className={cn(getStatusBadgeClass(status.status))}>
            <span className={cn(getStatusTextClass(status.status))}>
              {status.status}
            </span>
          </div>
        </div>

        {/* Training Progress */}
        {status.status === "training" && status.total_epochs && (
          <div className={styles.trainingProgress}>
            <div className={styles.progressBar}>
              <div
                className={styles.progressBarFill}
                style={{ width: `${((status.epoch || 0) / status.total_epochs) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Metrics */}
        {(status.loss !== undefined || status.accuracy !== undefined) && (
          <div className={styles.metricsGrid}>
            {status.loss !== undefined && (
              <div className={styles.metricCard}>
                <p className={styles.metricLabel}>Loss</p>
                <p className={styles.metricValue}>{status.loss.toFixed(4)}</p>
              </div>
            )}
            {status.accuracy !== undefined && (
              <div className={styles.metricCard}>
                <p className={styles.metricLabel}>Accuracy</p>
                <p className={styles.metricValuePrimary}>{(status.accuracy * 100).toFixed(1)}%</p>
              </div>
            )}
          </div>
        )}
      </div>
    </ShimmerBorder>
  );
}
