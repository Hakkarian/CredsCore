"use client";

import { useState } from "react";
import { ApplicantData } from "@/lib/api";
import { LabelInput } from "@/components/ui/label-input";
import { cn } from "@/lib/utils";
import styles from "./input-form.module.scss";

interface InputFormProps {
  formData: ApplicantData;
  onFormDataChange: (data: ApplicantData) => void;
  onSubmit: (data: ApplicantData) => void;
  isPending: boolean;
  submitLabel?: string;
}

export function InputForm({ formData, onFormDataChange, onSubmit, isPending, submitLabel = "Predict Risk" }: InputFormProps) {
  const [editValues, setEditValues] = useState<Record<string, string>>(
    () => Object.fromEntries(Object.entries(formData).map(([k, v]) => [k, String(v)]))
  );

  // Notify parent of changes in real-time (debounced)
  const notifyChange = (newValues: Record<string, string>) => {
    const parsedData = Object.fromEntries(
      Object.entries(formData).map(([key]) => [key, parseFloat(newValues[key] ?? "0") || 0])
    ) as unknown as ApplicantData;
    onFormDataChange(parsedData);
  };

  const handleChange = (key: string, value: string) => {
    const newValues = { ...editValues, [key]: value };
    setEditValues(newValues);
    notifyChange(newValues);
  };

  const handleSubmit = () => {
    const parsedData = Object.fromEntries(
      Object.entries(formData).map(([key]) => [key, parseFloat(editValues[key] ?? "0") || 0])
    ) as unknown as ApplicantData;

    onFormDataChange(parsedData);
    onSubmit(parsedData);
  };

  const formatLabel = (key: string) =>
    key
      .replace(/([A-Z])/g, " $1")
      .replace(/(\d+)([A-Z])/g, "$1 $2")
      .replace(/(\d),(\d)/g, "$1-$2")
      .trim();

  return (
    <div className={styles.card}>
      <h2 className={styles.cardTitle}>Applicant Data</h2>
      <div className={styles.fieldsContainer}>
        {Object.keys(formData).map((key) => (
          <LabelInput
            key={key}
            label={formatLabel(key)}
            type="number"
            value={editValues[key] ?? ""}
            onChange={(e) => handleChange(key, e.target.value)}
            step="any"
            className="[&_input]:[appearance:textfield] [&_input]:[&::-webkit-outer-spin-button]:appearance-none [&_input]:[&::-webkit-inner-spin-button]:appearance-none"
          />
        ))}
      </div>
      <button
        onClick={handleSubmit}
        disabled={isPending}
        className={cn(styles.submitButton, isPending && styles.submitButtonPending)}
      >
        {isPending ? (
          <span className={styles.submitButtonPending}>
            <svg className={styles.spinner} viewBox="0 0 24 24">
              <circle className={styles.spinnerCircle} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className={styles.spinnerPath} fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span>Analyzing...</span>
          </span>
        ) : (
          submitLabel
        )}
      </button>
    </div>
  );
}
