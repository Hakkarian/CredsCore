"use client";

import { useState } from "react";
import { api, ApplicantData } from "@/lib/api";

interface InputFormProps {
  formData: Record<string, number>;
  onFormDataChange: (data: Record<string, number>) => void;
  onResult: (result: any) => void;
  isLoading: boolean;
  onLoadingChange: (loading: boolean) => void;
}

const DEFAULT_FORM_DATA = {
  RevolvingUtilizationOfUnsecuredLines: 0.766,
  age: 45,
  NumberOfTime30_59DaysPastDueNotWorse: 2,
  DebtRatio: 0.803,
  MonthlyIncome: 9120,
  NumberOfOpenCreditLinesAndLoans: 13,
  NumberOfTimes90DaysLate: 0,
  NumberRealEstateLoansOrLines: 6,
  NumberOfTime60_89DaysPastDueNotWorse: 0,
  NumberOfDependents: 2,
};

const MOCK_RESULT = {
  prediction: 0,
  default_probability: 0.3427,
  risk_level: "medium",
  message: "Low risk - approved",
  top_risk_factors: [
    { feature: "NumberOfTime30-59DaysPastDueNotWorse", shap_value: 0.9805, impact: "increases_risk" },
    { feature: "RevolvingUtilizationOfUnsecuredLines", shap_value: 0.9103, impact: "increases_risk" },
    { feature: "NumberRealEstateLoansOrLines", shap_value: 0.6498, impact: "increases_risk" },
    { feature: "DebtRatio", shap_value: 0.3053, impact: "increases_risk" },
    { feature: "NumberOfTimes90DaysLate", shap_value: -0.1003, impact: "decreases_risk" },
  ],
};

export function InputForm({ formData, onFormDataChange, onResult, isLoading, onLoadingChange }: InputFormProps) {
  const handleSubmit = async () => {
    onLoadingChange(true);
    try {
      const data: ApplicantData = Object.fromEntries(
        Object.entries(formData).map(([key, value]) => [key, value])
      ) as unknown as ApplicantData;
      const response = await api.predict(data);
      onResult(response);
    } catch {
      onResult(MOCK_RESULT);
    }
    onLoadingChange(false);
  };

  const handleFieldChange = (key: string, value: string) => {
    onFormDataChange({ ...formData, [key]: parseFloat(value) || 0 });
  };

  return (
    <div className="card sticky top-28">
      <h2 className="font-display text-2xl font-bold text-white mb-6">Applicant Data</h2>
      <div className="space-y-4 max-h-[calc(100vh-16rem)] overflow-y-auto pr-2">
        {Object.entries(formData).map(([key, value]) => (
          <div key={key} className="flex flex-col">
            <label className="block text-sm font-medium text-gray-400 mb-1">
              {key.replace(/([A-Z])/g, " $1").trim()}
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => handleFieldChange(key, e.target.value)}
              className="w-full px-4 py-2 rounded-xl border border-card-border focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-300 bg-card-bg text-white text-left"
            />
          </div>
        ))}
      </div>
      <button
        onClick={handleSubmit}
        disabled={isLoading}
        className="w-full mt-6 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <span className="flex items-center justify-center space-x-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
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