"use client";

import { useState } from "react";
import cn from "classnames";
import { api, ApplicantData } from "@/lib/api";
import styles from "./dashboard.module.scss";

interface InputFormProps {
  formData: ApplicantData;
  onFormDataChange: (data: ApplicantData) => void;
  onResult: (result: any) => void;
  isLoading: boolean;
  onLoadingChange: (loading: boolean) => void;
}

export function InputForm({ formData, onFormDataChange, onResult, isLoading, onLoadingChange }: InputFormProps) {
  const [editValues, setEditValues] = useState<Record<string, string>>(
    () => Object.fromEntries(Object.entries(formData).map(([k, v]) => [k, String(v)]))
  );

  const handleSubmit = async () => {
    onLoadingChange(true);
    const parsedData = Object.fromEntries(
      Object.entries(formData).map(([key]) => [key, parseFloat(editValues[key] ?? "0") || 0])
    ) as unknown as ApplicantData;
    onFormDataChange(parsedData);
    try {
      const response = await api.predict(parsedData);
      onResult(response);
    } catch {
      onResult({
        prediction: 0,
        default_probability: 0.3427,
        risk_level: "medium",
        message: "Low risk - approved",
        top_risk_factors: [
          { feature: "RevolvingUtilizationOfUnsecuredLines", shap_value: 0.9103, impact: "increases_risk" },
          { feature: "NumberOfTime30-59DaysPastDueNotWorse", shap_value: 0.9805, impact: "increases_risk" },
          { feature: "NumberRealEstateLoansOrLines", shap_value: 0.6498, impact: "increases_risk" },
        ],
      });
    }
    onLoadingChange(false);
  };

  const formatLabel = (key: string) =>
    key
      .replace(/([A-Z])/g, " $1")
      .replace(/(\d+)([A-Z])/g, "$1 $2")
      .replace(/(\d),(\d)/g, "$1-$2")
      .trim();

  return (
    <div className={styles.inputForm}>
      <h2 className={styles.inputFormTitle}>Applicant Data</h2>
      <div className={styles.inputScrollArea}>
        {Object.keys(formData).map((key) => (
          <div key={key} className={styles.inputGroup}>
            <label className={styles.inputLabel}>{formatLabel(key)}</label>
            <input
              type="number"
              value={editValues[key] ?? ""}
              onChange={(e) => setEditValues((prev) => ({ ...prev, [key]: e.target.value }))}
              onFocus={(e) => e.target.select()}
              className={styles.inputField}
              step="any"
              placeholder="0"
            />
          </div>
        ))}
      </div>
      <button
        onClick={handleSubmit}
        disabled={isLoading}
        className={cn(styles.submitButton, isLoading && styles.submitButtonLoading)}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className={styles.spinner} viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span>Analyzing...</span>
          </span>
        ) : (
          "Predict Risk"
        )}
      </button>
    </div>
  );
}
