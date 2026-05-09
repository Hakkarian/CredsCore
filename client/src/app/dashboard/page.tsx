"use client";

import { useState } from "react";
import { DashboardHeader, PageHeader, TabBar, DASHBOARD_TABS, type DashboardTabId } from "@/components/dashboard/dashboard-header";
import { InputForm } from "@/components/dashboard/input-form";
import { PredictionResults } from "@/components/dashboard/results";
import { GroupsPanel } from "@/components/dashboard/groups-panel";
import { DriftPanel } from "@/components/dashboard/drift-panel";
import { SimilarTable } from "@/components/dashboard/similar-table";
import { SimilarCarousel } from "@/components/dashboard/similar-carousel";
import { InsightsPanel } from "@/components/insights/insights-panel";
import { AgenticPanel } from "@/components/agentic/agentic-panel";
import { SocialCapitalPanel } from "@/components/social/social-capital-panel";
import { GanPanel } from "@/components/synthetic-data/gan-panel";
import { usePredictMutation, useFraudSimilarMutation } from "@/hooks/use-credit-api";
import { ApplicantData, type PredictionResult, type EnrichedSimilarApplicant } from "@/lib/api";
import styles from "./page.module.scss";

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
  const [activeTab, setActiveTab] = useState<DashboardTabId>("predict");
  const [formData, setFormData] = useState<ApplicantData>(DEFAULT_FORM_DATA);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [similarApplicants, setSimilarApplicants] = useState<EnrichedSimilarApplicant[]>([]);

  const predictMutation = usePredictMutation();
  const fraudSimilarMutation = useFraudSimilarMutation();

  const handleSubmit = (data: ApplicantData) => {
    predictMutation.mutate(data, {
      onSuccess: (result) => {
        setPrediction(result);
      },
    });
    fraudSimilarMutation.mutate(data, {
      onSuccess: (result) => {
        // Map fraud similar results to EnrichedSimilarApplicant format
        const mapped = result.similar_applicants.map((item: any) => ({
          index: item.index,
          similarityScore: 1 - item.distance, // Convert distance to similarity
          defaultLabel: item.default,
          trendData: [{ value: 0.5 }, { value: 1 - item.distance }],
        }));
        setSimilarApplicants(mapped);
      },
    });
  };

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <DashboardHeader title="Credit Risk Dashboard" subtitle="AI-powered credit scoring and analysis" />
        <PageHeader title="Credit Risk Dashboard" subtitle="AI-powered credit scoring and analysis" />

        <div className={styles.tabBarWrapper}>
          <TabBar tabs={DASHBOARD_TABS} activeTab={activeTab} onTabChange={(id) => setActiveTab(id as DashboardTabId)} />
        </div>

        <div className={styles.tabContent}>
          {activeTab === "predict" && (
            <>
              <section className={styles.section}>
                <InputForm
                  formData={formData}
                  onFormDataChange={setFormData}
                  onSubmit={handleSubmit}
                  isPending={predictMutation.isPending}
                />
              </section>

              {prediction && (
                <section className={styles.sectionAnimated}>
                  <PredictionResults result={prediction} />
                </section>
              )}

              {similarApplicants.length > 0 && (
                <section className={styles.sectionAnimatedGrid2}>
                  <SimilarCarousel data={similarApplicants} />
                  <SimilarTable data={similarApplicants} />
                </section>
              )}

              {formData && (
                <section className={styles.sectionAnimatedGrid2}>
                  <InsightsPanel applicantId="default" features={formData} />
                  <AgenticPanel applicantId="default" features={formData} />
                </section>
              )}

              {formData && (
                <section className={styles.sectionAnimated}>
                  <SocialCapitalPanel data={null} networkData={null} />
                </section>
              )}
            </>
          )}

          {activeTab === "similar" && formData && (
            <section className={styles.sectionAnimatedGrid2}>
              <SimilarCarousel data={similarApplicants} />
              <SimilarTable data={similarApplicants} />
            </section>
          )}

          {activeTab === "synthetic" && (
            <section className={styles.sectionAnimated}>
              <GanPanel />
            </section>
          )}

          {activeTab === "groups" && (
            <section className={styles.section}>
              <GroupsPanel />
            </section>
          )}

          {activeTab === "drift" && (
            <section className={styles.section}>
              <DriftPanel />
            </section>
          )}

          {activeTab === "insights" && formData && (
            <section className={styles.sectionAnimated}>
              <InsightsPanel applicantId="default" features={formData} />
            </section>
          )}

          {activeTab === "agentic" && formData && (
            <section className={styles.sectionAnimated}>
              <AgenticPanel applicantId="default" features={formData} />
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
