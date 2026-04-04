"use client";

import { PredictionResult } from "@/lib/api";
import { STATS, RECENT_PREDICTIONS } from "./dashboard-header";

interface PredictionResultsProps {
  result: PredictionResult | null;
}

export function PredictionResults({ result }: PredictionResultsProps) {
  if (!result) return null;

  return (
    <div className="card animate-scale-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="font-display text-2xl font-bold text-white mb-2">Prediction Result</h2>
          <p className="text-gray-400">{result.message}</p>
        </div>
        <div className={`px-4 py-2 rounded-full font-semibold ${
          result.risk_level === "low" ? "bg-green-500/20 text-green-400" :
          result.risk_level === "medium" ? "bg-yellow-500/20 text-yellow-400" :
          "bg-red-500/20 text-red-400"
        }`}>
          {result.risk_level.toUpperCase()} RISK
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-primary/10 rounded-2xl p-6 flex flex-col justify-center">
          <div className="text-4xl font-bold text-white mb-1">{(result.default_probability * 100).toFixed(1)}%</div>
          <div className="text-gray-400 text-sm">Default Probability</div>
        </div>
        <div className="bg-primary/10 rounded-2xl p-6 flex flex-col justify-center">
          <div className="text-4xl font-bold text-white mb-1">{result.prediction === 0 ? "APPROVE" : "DENY"}</div>
          <div className="text-gray-400 text-sm">Recommendation</div>
        </div>
      </div>
      <h3 className="font-display text-xl font-bold text-white mb-4">Top Risk Factors</h3>
      <div className="space-y-3">
        {result.top_risk_factors.map((factor, i) => (
          <div key={i} className="flex items-center space-x-4 align-middle">
            <div className="w-48 text-sm text-gray-400 truncate">{factor.feature}</div>
            <div className="flex-1 h-8 bg-card-bg rounded-lg overflow-hidden relative">
              <div
                className={`h-full rounded-lg transition-all duration-500 ${
                  factor.impact === "increases_risk" ? "bg-gradient-to-r from-red-500 to-red-600" :
                  "bg-gradient-to-r from-green-500 to-green-600"
                }`}
                style={{ width: `${Math.min(Math.abs(factor.shap_value) * 50, 100)}%` }}
              />
            </div>
            <div className="w-20 text-right text-sm font-medium text-white">{factor.shap_value.toFixed(4)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function StatsGrid() {
  return (
    <div className="grid md:grid-cols-3 gap-6">
      {STATS.map((stat, i) => (
        <div key={i} className="card flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <span className="text-3xl">{stat.icon}</span>
            <span className={`text-sm font-medium ${stat.trend.startsWith("+") ? "text-green-400" : "text-red-400"}`}>{stat.trend}</span>
          </div>
          <div className="font-display text-2xl font-bold text-white mb-1">{stat.value}</div>
          <div className="text-gray-400 text-sm">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}

export function RecentActivityTable() {
  const getRiskColor = (risk: string) => risk === "Low" ? "bg-green-500/20 text-green-400" :
    risk === "Medium" ? "bg-yellow-500/20 text-yellow-400" : "bg-red-500/20 text-red-400";
  const getStatusColor = (status: string) => status === "Approved" ? "bg-green-500/20 text-green-400" :
    status === "Denied" ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400";

  return (
    <div className="card">
      <h3 className="font-display text-xl font-bold text-white mb-4">Recent Predictions</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-card-border">
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">ID</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Probability</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Risk Level</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Time</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Status</th>
            </tr>
          </thead>
          <tbody>
            {RECENT_PREDICTIONS.map((row, i) => (
              <tr key={i} className="border-b border-card-border/50 hover:bg-white/5 transition-colors">
                <td className="py-3 px-4 text-sm text-white font-medium">{row.id}</td>
                <td className="py-3 px-4 text-sm text-gray-400">{row.prob}</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-1 rounded-lg text-xs font-medium ${getRiskColor(row.risk)}`}>{row.risk}</span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-400">{row.time}</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-1 rounded-lg text-xs font-medium ${getStatusColor(row.status)}`}>{row.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}