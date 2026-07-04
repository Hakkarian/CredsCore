"use client";

import { BarChart3, Users, FlaskConical, Search, Bot, CheckCircle2, Zap } from "lucide-react";
import { FloatingNav } from "@/components/ui/floating-nav";
import { TextGenerateEffect } from "@/components/ui/text-generate-effect";
import { Tabs } from "@/components/ui/tabs";
import styles from "./dashboard-header.module.scss";

// Navigation items shared across dashboard
export const NAV_ITEMS = [
  { name: "Home", link: "/" },
  { name: "Docs", link: "/docs" },
];

// Tab definitions for the dashboard
export const DASHBOARD_TABS = [
  { id: "predict", label: "Predict", icon: BarChart3 },
  { id: "similar", label: "Similar", icon: Users },
  { id: "synthetic", label: "Synthetic", icon: FlaskConical },
  { id: "insights", label: "Insights", icon: Search },
  { id: "agentic", label: "Agentic", icon: Bot },
] as const;

export type DashboardTabId = (typeof DASHBOARD_TABS)[number]["id"];

interface DashboardHeaderProps {
  title: string;
  subtitle: string;
}

export function DashboardHeader({ title, subtitle }: DashboardHeaderProps) {
  return <FloatingNav navItems={NAV_ITEMS} />;
}

interface PageHeaderProps {
  title: string;
  subtitle: string;
}

export function PageHeader({ title, subtitle }: PageHeaderProps) {
  return (
    <div className={styles.pageHeader}>
      <h1 className={styles.pageTitle}>
        <TextGenerateEffect words={title} />
      </h1>
      <p className={styles.pageSubtitle}>{subtitle}</p>
    </div>
  );
}

interface TabBarProps {
  tabs: readonly { id: string; label: string; icon: React.ComponentType<{ className?: string }> }[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export function TabBar({ tabs, activeTab, onTabChange }: TabBarProps) {
  const aceternityTabs = tabs.map((tab) => {
    const Icon = tab.icon;
    return {
      title: (
        <>
          <Icon className={styles.tabIcon} />
          {tab.label}
        </>
      ),
      value: tab.id,
    };
  });

  return (
    <div className={styles.tabBar}>
      <Tabs
        tabs={aceternityTabs}
        activeTab={activeTab}
        onChange={onTabChange}
      />
    </div>
  );
}

// Stats data used by StatsGrid in results.tsx
export const STATS = [
  { icon: BarChart3, value: "1,247", label: "Total Applications", trend: "+12.5%" },
  { icon: CheckCircle2, value: "89.3%", label: "Approval Rate", trend: "+2.1%" },
  { icon: Zap, value: "0.8s", label: "Avg Response Time", trend: "-15.2%" },
];

// Recent predictions data used by RecentActivityTable in results.tsx
export const RECENT_PREDICTIONS = [
  { id: "APP-001", name: "John D.", risk: "low" as const, prob: "12%", status: "approved" as const },
  { id: "APP-002", name: "Sarah M.", risk: "medium" as const, prob: "45%", status: "review" as const },
  { id: "APP-003", name: "Mike R.", risk: "high" as const, prob: "78%", status: "denied" as const },
  { id: "APP-004", name: "Lisa K.", risk: "low" as const, prob: "8%", status: "approved" as const },
  { id: "APP-005", name: "Tom W.", risk: "medium" as const, prob: "52%", status: "review" as const },
];