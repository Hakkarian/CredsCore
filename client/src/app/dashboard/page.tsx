"use client";

import { useState } from "react";
import { DashboardHeader, PageHeader, TabBar, DASHBOARD_TABS } from "@/components/dashboard/dashboard-header";
import { InputForm } from "@/components/dashboard/input-form";
import { PredictionResults, StatsGrid, RecentActivityTable } from "@/components/dashboard/results";
import { PredictionResult } from "@/lib/api";

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

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("predict");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [formData, setFormData] = useState(DEFAULT_FORM_DATA);

  return (
    <div className="min-h-screen bg-dark-green">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 gradient-mesh opacity-20" />
        <div className="absolute top-20 left-20 w-72 h-72 bg-primary/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-accent-pink/10 rounded-full blur-3xl animate-float" style={{ animationDelay: "1.5s" }} />
      </div>
      <DashboardHeader title="CredsCore" subtitle="Dashboard" />
      <div className="pt-24 p-8">
        <div className="max-w-7xl mx-auto">
          <PageHeader title="Credit Risk Dashboard" subtitle="Real-time credit risk assessment and monitoring" />
          <TabBar tabs={DASHBOARD_TABS} activeTab={activeTab} onTabChange={setActiveTab} />
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1">
              <InputForm formData={formData} onFormDataChange={setFormData} onResult={setResult} isLoading={isLoading} onLoadingChange={setIsLoading} />
            </div>
            <div className="lg:col-span-2 space-y-6">
              <PredictionResults result={result} />
              <StatsGrid />
              <RecentActivityTable />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}