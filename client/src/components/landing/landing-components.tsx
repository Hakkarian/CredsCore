"use client";

import { useEffect, useState } from "react";

interface AnimatedBackgroundProps {
  isLoaded: boolean;
}

export function Navigation({ isLoaded }: { isLoaded: boolean }) {
  const navItems = ["Features", "Docs", "Dashboard", "API"];
  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-700 ${isLoaded ? "translate-y-0 opacity-100" : "-translate-y-full opacity-0"}`}>
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="glass-dark rounded-full px-6 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 gradient-primary rounded-xl flex items-center justify-center shadow-lg"><span className="text-white font-bold text-lg">CC</span></div>
            <span className="font-display font-bold text-xl text-white">CredsCore</span>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <a key={item} href={item === "Docs" ? "/docs" : item === "Dashboard" ? "/dashboard" : "#"} className="text-gray-300 hover:text-white transition-colors duration-300 font-medium relative group">
                {item}<span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary transition-all duration-300 group-hover:w-full" />
              </a>
            ))}
          </div>
          <button className="btn-primary">Get Started</button>
        </div>
      </div>
    </nav>
  );
}

export function HeroSection({ isLoaded }: { isLoaded: boolean }) {
  return (
    <section className="pt-32 pb-20 px-6">
      <div className="max-w-7xl mx-auto text-center">
        <div className={`inline-flex items-center space-x-2 glass px-4 py-2 rounded-full mb-8 transition-all duration-700 ${isLoaded ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"}`}>
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" /><span className="text-sm font-medium text-gray-300">AI-Powered Credit Scoring</span>
        </div>
        <h1 className={`font-display text-5xl md:text-7xl font-bold text-white mb-6 leading-tight transition-all duration-700 delay-100 ${isLoaded ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"}`}>
          Smart Credit<br /><span className="bg-gradient-to-r from-primary via-accent-cyan to-accent-lavender bg-clip-text text-transparent">Risk Assessment</span>
        </h1>
        <p className={`text-xl text-gray-400 max-w-2xl mx-auto mb-12 transition-all duration-700 delay-200 ${isLoaded ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"}`}>
          Leverage LightGBM, SHAP explanations, and FAISS vector search to make accurate, explainable credit decisions in real-time.
        </p>
        <div className={`flex flex-col sm:flex-row items-center justify-center gap-4 transition-all duration-700 delay-300 ${isLoaded ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"}`}>
          <button className="btn-primary text-lg px-8 py-4">Try Live Demo</button>
          <button className="btn-secondary text-lg px-8 py-4">View Documentation</button>
        </div>
      </div>
    </section>
  );
}

export function HeroVisual({ isLoaded }: { isLoaded: boolean }) {
  const icons = ["📊", "🎯", "⚡"];
  return (
    <div className={`mt-20 relative transition-all duration-1000 delay-500 ${isLoaded ? "translate-y-0 opacity-100 scale-100" : "translate-y-20 opacity-0 scale-95"}`}>
      <div className="card max-w-4xl mx-auto shadow-2xl">
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="h-4 bg-primary/30 rounded-full shimmer" /><div className="h-4 bg-accent-cyan/30 rounded-full shimmer" style={{ animationDelay: "0.2s" }} /><div className="h-4 bg-accent-lavender/30 rounded-full shimmer" style={{ animationDelay: "0.4s" }} />
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="w-12 h-12 gradient-accent rounded-xl flex items-center justify-center text-2xl shadow-lg animate-bounce-subtle" style={{ animationDelay: `${i * 0.3}s` }}>{icons[i - 1]}</div>
              <div className="flex-1 space-y-2"><div className="h-3 bg-white/20 rounded-full w-3/4" /><div className="h-3 bg-white/10 rounded-full w-1/2" /></div>
            </div>
          ))}
        </div>
      </div>
      <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-3/4 h-8 bg-primary/10 rounded-full blur-xl" />
    </div>
  );
}

export function StatsGrid() {
  const stats = [{ value: "99.2%", label: "Accuracy", icon: "🎯" }, { value: "< 100ms", label: "Response Time", icon: "⚡" }, { value: "150K+", label: "Training Samples", icon: "📊" }, { value: "5", label: "Use Cases", icon: "🔧" }];
  return (
    <section className="py-20 px-6">
      <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <div key={i} className="card text-center group" style={{ animationDelay: `${i * 0.1}s` }}>
            <div className="text-4xl mb-3 group-hover:scale-110 transition-transform duration-300">{stat.icon}</div>
            <div className="font-display text-3xl font-bold text-white mb-1">{stat.value}</div>
            <div className="text-gray-400 text-sm">{stat.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

export function FeaturesSection({ activeFeature, onFeatureChange }: { activeFeature: number; onFeatureChange: (i: number) => void }) {
  const features = [{ icon: "🎯", title: "Risk Prediction", description: "Advanced ML models predict credit default probability with high accuracy", color: "from-primary to-accent-pink" }, { icon: "🔍", title: "Similar Applicants", description: "FAISS vector search finds similar past applicants for better insights", color: "from-accent-pink to-accent-lavender" }, { icon: "📊", title: "Explainable AI", description: "SHAP explanations provide clear reasoning behind every decision", color: "from-accent-lavender to-accent-gold" }, { icon: "📈", title: "Drift Monitoring", description: "Real-time detection of data distribution changes", color: "from-accent-gold to-primary" }];
  return (
    <section className="py-20 px-6" id="features">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="font-display text-4xl md:text-5xl font-bold text-white mb-4">Powerful Features</h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">Everything you need for intelligent credit risk assessment</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, i) => (
            <div key={i} className={`card cursor-pointer ${activeFeature === i ? "ring-2 ring-primary shadow-lg shadow-primary/20" : ""}`} onClick={() => onFeatureChange(i)} style={{ animationDelay: `${i * 0.15}s` }}>
              <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-3xl mb-6 shadow-lg`}>{feature.icon}</div>
              <h3 className="font-display text-xl font-bold text-white mb-3">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function CTASection() {
  return (
    <section className="py-20 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="gradient-primary rounded-3xl p-12 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-accent-gold/20 via-accent-pink/20 to-accent-lavender/20" />
          <div className="relative z-10">
            <h2 className="font-display text-4xl font-bold text-white mb-4">Ready to Transform Your Credit Decisions?</h2>
            <p className="text-white/80 text-lg mb-8 max-w-2xl mx-auto">Start making smarter, faster, and more explainable credit decisions today.</p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button className="bg-white text-primary px-8 py-4 rounded-full font-semibold text-lg shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300">Start Free Trial</button>
              <button className="border-2 border-white/30 text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-white/10 transform hover:-translate-y-1 transition-all duration-300">Schedule Demo</button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export function Footer() {
  return (
    <footer className="py-12 px-6 border-t border-card-border">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between">
        <div className="flex items-center space-x-3 mb-4 md:mb-0">
          <div className="w-10 h-10 gradient-primary rounded-xl flex items-center justify-center"><span className="text-white font-bold text-lg">CC</span></div>
          <span className="font-display font-bold text-xl text-white">CredsCore</span>
        </div>
        <div className="text-gray-400 text-sm">© 2026 CredsCore. AI-Powered Credit Scoring.</div>
      </div>
    </footer>
  );
}