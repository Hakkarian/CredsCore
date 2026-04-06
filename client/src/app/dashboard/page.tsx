"use client";

import { useState } from "react";
import { SiteHeader } from "@/components/layout/site-header";
import { PageHeader, TabBar, DASHBOARD_TABS } from "@/components/dashboard/dashboard-header";
import { InputForm } from "@/components/dashboard/input-form";
import { PredictionResults, StatsGrid, RecentActivityTable } from "@/components/dashboard/results";
import { PredictionResult, ApplicantData } from "@/lib/api";
import styles from "@/components/dashboard/dashboard.module.scss";

const DEFAULT_FORM_DATA: ApplicantData = {
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

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("predict");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [formData, setFormData] = useState(DEFAULT_FORM_DATA);

  return (
    <div className={styles.dashboard}>
      <SiteHeader activePage="dashboard" />
      <main className={styles.main}>
        <div className={styles.container}>
          <PageHeader title="Credit Risk Dashboard" subtitle="Real-time credit risk assessment and monitoring" />
          <TabBar tabs={DASHBOARD_TABS} activeTab={activeTab} onTabChange={setActiveTab} />
          <div className={styles.content}>
            <div className={styles.sidebar}>
              <InputForm formData={formData} onFormDataChange={setFormData} onResult={setResult} isLoading={isLoading} onLoadingChange={setIsLoading} />
            </div>
            <div className={styles.results}>
              <PredictionResults result={result} />
              <StatsGrid />
              <RecentActivityTable />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
