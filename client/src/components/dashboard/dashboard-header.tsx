"use client";

import cn from "classnames";
import styles from "./dashboard.module.scss";

interface DashboardHeaderProps {
  title: string;
  subtitle: string;
}

export function DashboardHeader({ title, subtitle }: DashboardHeaderProps) {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-green/90 backdrop-blur-md border-b border-card-border/30">
      <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
        <a href="/" className="flex items-center space-x-3">
          <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-dark-green font-bold text-sm">CC</span>
          </div>
          <span className="font-display font-bold text-lg text-white">{title}</span>
        </a>
        <div className="flex items-center space-x-6">
          <a href="/" className="text-gray-400 hover:text-primary transition-colors duration-200">
            Home
          </a>
          <a href="/dashboard" className="text-primary font-medium">
            Dashboard
          </a>
          <a href="/docs" className="text-gray-400 hover:text-primary transition-colors duration-200">
            Docs
          </a>
        </div>
      </div>
    </nav>
  );
}

interface PageHeaderProps {
  title: string;
  subtitle: string;
}

export function PageHeader({ title, subtitle }: PageHeaderProps) {
  return (
    <div className={styles.pageHeader}>
      <h1 className={styles.pageTitle}>{title}</h1>
      <p className={styles.pageSubtitle}>{subtitle}</p>
    </div>
  );
}

interface TabBarProps {
  tabs: { id: string; label: string; icon: string }[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export function TabBar({ tabs, activeTab, onTabChange }: TabBarProps) {
  return (
    <div className={styles.tabBar}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={cn(
            activeTab === tab.id ? styles.tabButtonActive : styles.tabButton
          )}
        >
          <span>{tab.icon}</span>
          <span>{tab.label}</span>
        </button>
      ))}
    </div>
  );
}

export const DASHBOARD_TABS = [
  { id: "predict", label: "Predict", icon: "\u{1F3AF}" },
  { id: "similar", label: "Similar", icon: "\u{1F50D}" },
  { id: "drift", label: "Drift", icon: "\u{1F4C8}" },
  { id: "groups", label: "Groups", icon: "\u{1F465}" },
];

export const STATS = [
  { label: "Total Predictions", value: "1,234", icon: "\u{1F4CA}", trend: "+12%" },
  { label: "Avg. Response Time", value: "87ms", icon: "\u{26A1}", trend: "-5%" },
  { label: "Accuracy Rate", value: "99.2%", icon: "\u{1F3AF}", trend: "+0.3%" },
];

export const RECENT_PREDICTIONS = [
  { id: "P-001", prob: "12.3%", risk: "Low", time: "2 min ago", status: "Approved" },
  { id: "P-002", prob: "45.7%", risk: "Medium", time: "5 min ago", status: "Review" },
  { id: "P-003", prob: "78.2%", risk: "High", time: "8 min ago", status: "Denied" },
  { id: "P-004", prob: "23.1%", risk: "Low", time: "12 min ago", status: "Approved" },
  { id: "P-005", prob: "56.8%", risk: "Medium", time: "15 min ago", status: "Review" },
];