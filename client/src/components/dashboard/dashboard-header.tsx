"use client";

interface DashboardHeaderProps {
  title: string;
  subtitle: string;
}

export function DashboardHeader({ title, subtitle }: DashboardHeaderProps) {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-dark">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <a href="/" className="flex items-center space-x-3">
          <div className="w-10 h-10 gradient-primary rounded-xl flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-lg">CC</span>
          </div>
          <span className="font-display font-bold text-xl text-white">CredsCore</span>
        </a>
        <div className="flex items-center space-x-6">
          <a href="/" className="text-gray-300 hover:text-white transition-colors">Home</a>
          <a href="/dashboard" className="text-white font-semibold">Dashboard</a>
          <a href="/docs" className="text-gray-300 hover:text-white transition-colors">Docs</a>
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
    <div className="mb-8 flex flex-col">
      <h1 className="font-display text-4xl font-bold text-white mb-2">{title}</h1>
      <p className="text-gray-400">{subtitle}</p>
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
    <div className="flex space-x-2 mb-8 items-center">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`px-6 py-3 rounded-full font-medium transition-all duration-300 flex items-center justify-center space-x-2 ${
            activeTab === tab.id ? "gradient-primary text-white shadow-lg" : "glass text-gray-300 hover:bg-white/10"
          }`}
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