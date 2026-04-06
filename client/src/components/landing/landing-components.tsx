"use client";

import { useEffect, useState } from "react";

const navItems = ["Features", "Docs", "Dashboard", "API"];

export function Navigation({ isLoaded }: { isLoaded: boolean }) {
  return (
    <header className={`sticky top-0 z-50 transition-all duration-700 ${isLoaded ? "translate-y-0 opacity-100" : "-translate-y-full opacity-0"}`}>
      <div className="mx-auto w-full px-8">
        <div className="flex items-center justify-between py-6">
          <a href="/" className="flex items-center gap-3">
            <div className="h-10 w-10 gradient-primary rounded-2xl flex items-center justify-center shadow-md">
              <span className="text-white font-bold">CC</span>
            </div>
            <span className="font-display font-bold text-xl text-white">CredsCore</span>
          </a>
          <nav className="hidden lg:flex items-center gap-8">
            {navItems.map((item) => (
              <a key={item} href={item === "Docs" ? "/docs" : item === "Dashboard" ? "/dashboard" : "#"} className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                {item}
              </a>
            ))}
          </nav>
          <div className="flex items-center gap-4">
            <a href="/dashboard" className="text-sm text-gray-300 hover:text-white">Sign In</a>
            <button className="btn-primary px-6 py-2.5 text-sm">Get Started</button>
          </div>
        </div>
      </div>
    </header>
  );
}

export function HeroSection({ isLoaded }: { isLoaded: boolean }) {
  return (
    <section className="px-8 py-16">
      <div className="mx-auto max-w-6xl grid md:grid-cols-2 gap-12 items-center">
        <div className={`space-y-6 transition-all duration-700 ${isLoaded ? "translate-x-0 opacity-100" : "-translate-x-10 opacity-0"}`}>
          <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full px-4 py-1.5">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm text-gray-300">AI-Powered Credit Scoring</span>
          </div>
          <h1 className="font-display text-5xl md:text-6xl font-bold text-white leading-tight">
            Credit Risk Analysis,{" "}
            <span className="text-primary">Reimagined</span>
          </h1>
          <p className="text-lg text-gray-400 max-w-lg">
            Make smarter lending decisions with LightGBM, SHAP explanations, and FAISS vector similarity search — all in real-time.
          </p>
          <div className="flex flex-wrap gap-4 pt-2">
            <a href="/dashboard" className="btn-primary px-8 py-3.5">Start Predicting</a>
            <a href="/docs" className="btn-secondary px-8 py-3.5">Read Docs</a>
          </div>
        </div>
        <div className={`transition-all duration-700 delay-200 ${isLoaded ? "translate-x-0 opacity-100" : "translate-x-10 opacity-0"}`}>
          <div className="card p-12 space-y-8">
            <h3 className="text-white font-semibold flex items-center gap-2 text-lg">
              📊 Applicant Analysis
            </h3>
            {[{ label: "Income Score", pct: 85 }, { label: "Credit History", pct: 92 }, { label: "Debt Ratio", pct: 67 }].map((item, i) => (
              <div key={i} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">{item.label}</span>
                  <span className="text-white font-medium">{item.pct}%</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full rounded-full bg-gradient-to-r from-primary to-accent-cyan" style={{ width: `${item.pct}%` }} />
                </div>
              </div>
            ))}
            <div className="pt-2 flex items-center gap-3">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-green-500/20 text-green-400 text-sm font-bold">✓</span>
              <span className="text-sm text-gray-300">Low Risk — Approved</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export function StatsGrid() {
  const stats = [
    { value: "99.2%", label: "Model Accuracy" },
    { value: "<100ms", label: "Inference Speed" },
    { value: "150K+", label: "Training Records" },
    { value: "5", label: "API Endpoints" },
  ];
  return (
    <section className="px-8 py-12">
      <div className="mx-auto max-w-6xl grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((s, i) => (
          <div key={i} className="card p-10 text-center md:text-left">
            <div className="font-display text-3xl font-bold text-white">{s.value}</div>
            <div className="text-sm text-gray-500 mt-1">{s.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

export function FeaturesSection({ activeFeature, onFeatureChange }: { activeFeature: number; onFeatureChange: (i: number) => void }) {
  const features = [
    { icon: "🎯", title: "Risk Prediction", desc: "LightGBM models deliver state-of-the-art default probability estimation." },
    { icon: "🔍", title: "Similarity Search", desc: "FAISS embeddings find historically similar applicants for context." },
    { icon: "📊", title: "Explainability", desc: "SHAP values break down every factor influencing a credit decision." },
    { icon: "📈", title: "Drift Detection", desc: "Monitor data shifts over time and retrain models proactively." },
  ];
  return (
    <section id="features" className="px-8 py-16">
      <div className="mx-auto max-w-6xl">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((f, i) => (
            <button
              key={i}
              className={`text-left p-10 rounded-2xl border transition-all duration-300 focus:outline-none ${activeFeature === i
                  ? "bg-primary/10 border-primary shadow-lg shadow-primary/10"
                  : "bg-card/50 border-card-border hover:border-primary/50"
                }`}
              onClick={() => onFeatureChange(i)}
            >
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="text-white font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

export function CTASection() {
  return (
    <section className="px-8 py-16">
      <div className="mx-auto max-w-4xl">
        <div className="gradient-primary rounded-3xl p-16 md:p-24 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-accent-gold/10 via-accent-pink/10 to-accent-lavender/10" />
          <div className="relative z-10 space-y-4">
            <h2 className="font-display text-3xl md:text-4xl font-bold text-white">
              Transform Your Credit Process
            </h2>
            <p className="text-white/70 max-w-xl mx-auto">
              Deploy intelligent scoring in minutes. No infrastructure, no training data — just predictions.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <a href="/dashboard" className="bg-white text-primary font-semibold px-8 py-3 rounded-full hover:shadow-xl transition-all">
                Start Free Trial
              </a>
              <a href="/docs" className="border border-white/20 text-white px-8 py-3 rounded-full hover:bg-white/10 transition-all">
                View API Docs
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export function Footer() {
  return (
    <footer className="px-8 py-10 border-t border-card-border">
      <div className="mx-auto max-w-6xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 gradient-primary rounded-xl flex items-center justify-center">
            <span className="text-white font-bold text-sm">CC</span>
          </div>
          <span className="font-display font-semibold text-white">CredsCore</span>
        </div>
        <span className="text-sm text-gray-500">&copy; 2026 CredsCore</span>
      </div>
    </footer>
  );
}