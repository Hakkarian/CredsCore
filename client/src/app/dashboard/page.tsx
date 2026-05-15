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
    fraudSimilarMutation.mutate({ data, k: 10 }, {
      onSuccess: (result) => {
        // Map fraud similar results to EnrichedSimilarApplicant format
        // Use exponential decay normalization for L2 distances which can be >1
        const mapped = result.similar_applicants.map((item: any) => {
          const normalized = item.distance <= 1
            ? Math.max(0, 1 - item.distance)
            : Math.max(0, Math.exp(-item.distance * 0.05));
          return {
            index: item.index,
            distance: item.distance,
            similarityScore: normalized,
            riskLevel: normalized >= 0.5 ? "high" as const : normalized >= 0.25 ? "medium" as const : "low" as const,
            defaultLabel: item.default,
            trendData: [{ value: 0.5 }, { value: normalized }],
          };
        });
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

              {!prediction && similarApplicants.length === 0 ? (
                <div className={styles.welcome}>
                  <p>No defaults detected — yet.</p>
                  <p>Be the first to train the model.</p>
                </div>
              ) : (
                <>
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
                      <InsightsPanel applicantId="default" features={formData} mlProbability={prediction?.default_probability} />
                      <AgenticPanel applicantId="default" features={formData} mlProbability={prediction?.default_probability} />
                    </section>
                  )}

                  {formData && (
                    <section className={styles.sectionAnimated}>
                      <SocialCapitalPanel applicantId="default" features={formData} />
                    </section>
                  )}
                </>
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
              <InsightsPanel applicantId="default" features={formData} mlProbability={prediction?.default_probability} />
            </section>
          )}

          {activeTab === "agentic" && formData && (
            <section className={styles.sectionAnimated}>
              <AgenticPanel applicantId="default" features={formData} mlProbability={prediction?.default_probability} />
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
