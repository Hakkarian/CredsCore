"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Target, Zap, BookOpen, Plug, Search, BarChart3, TrendingUp, Users, FileText } from "lucide-react";
import { FloatingNav } from "@/components/ui/floating-nav";
import { SpotlightHero } from "@/components/ui/spotlight";
import { TextGenerateEffect } from "@/components/ui/text-generate-effect";
import { ShimmerTiltCard } from "@/components/ui/shimmer-tilt-card";
import { BackgroundBeams } from "@/components/ui/background-beams";
import styles from "./landing-components.module.scss";

/* ------------------------------------------------------------------ */
/* Navigation */
/* ------------------------------------------------------------------ */

const navItems = [
  { name: "Home", link: "/" },
  { name: "Docs", link: "/docs" },
];
// Note: FloatingNav always appends a highlighted "Dashboard" CTA at the end,
// so Dashboard must not be included here (it would render twice).

function Navigation() {
  return <FloatingNav navItems={navItems} />;
}

/* ------------------------------------------------------------------ */
/* Hero */
/* ------------------------------------------------------------------ */

function HeroSection() {
  return (
    <section className={styles.hero}>
      {/* Animated spotlight beam */}
      <SpotlightHero className="left-0 top-0 h-full w-full" fill="#F3CA40" />

      {/* Radial glow */}
      <div className={styles.heroRadialGlow}>
        <div className={styles.heroGlowOrb} />
      </div>

      <div className={styles.heroContent}>
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className={styles.heroBadge}
        >
          <span className={styles.heroBadgeDot} />
          AI-Powered Credit Scoring
        </motion.div>

        {/* Headline */}
        <TextGenerateEffect
          words="Credit Intelligence Redefined"
          className="text-5xl font-bold leading-tight tracking-tight text-neutral-100 md:text-7xl"
        />

        {/* Sub-text */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.2 }}
          className={styles.heroSubtitle}
        >
          Make smarter lending decisions with LightGBM, SHAP explanations, and
          FAISS vector similarity search — all in real-time.
        </motion.p>

        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.5 }}
          className={styles.heroCtas}
        >
          <Link
            href="/dashboard"
            className={styles.ctaPrimary}
          >
            Start Predicting
          </Link>
          <Link
            href="/docs"
            className={styles.ctaSecondary}
          >
            Read Docs
          </Link>
        </motion.div>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Stats */
/* ------------------------------------------------------------------ */

const stats = [
  { value: "99.2%", label: "Model Accuracy", icon: Target, trend: "+0.4%" },
  { value: "<100ms", label: "Inference Speed", icon: Zap, trend: "-12ms" },
  { value: "150K+", label: "Training Records", icon: BookOpen, trend: "+12K" },
  { value: "5", label: "API Endpoints", icon: Plug, trend: "Stable" },
];

function StatsSection() {
  return (
    <section className={styles.statsSection}>
      <div className={styles.statsGrid}>
        {stats.map((s, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
          >
            <ShimmerTiltCard className="h-full">
              <div className={styles.statCard}>
                <div className={styles.statHeader}>
                  <span className={styles.statIcon}>
                    <s.icon className={styles.statIconSvg} />
                  </span>
                  <span className={styles.statTrend}>
                    {s.trend}
                  </span>
                </div>
                <span className={styles.statValue}>
                  {s.value}
                </span>
                <span className={styles.statLabel}>{s.label}</span>
              </div>
            </ShimmerTiltCard>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Features */
/* ------------------------------------------------------------------ */

const features = [
  {
    icon: Target,
    title: "Risk Prediction",
    desc: "LightGBM models deliver state-of-the-art default probability estimation.",
  },
  {
    icon: Search,
    title: "Similarity Search",
    desc: "FAISS embeddings find historically similar applicants for context.",
  },
  {
    icon: BarChart3,
    title: "Explainability",
    desc: "SHAP values break down every factor influencing a credit decision.",
  },
  {
    icon: TrendingUp,
    title: "Drift Detection",
    desc: "Monitor data shifts over time and retrain models proactively.",
  },
  {
    icon: Users,
    title: "Peer Groups",
    desc: "Compare applicants against peer groups to refine scoring accuracy.",
  },
  {
    icon: FileText,
    title: "Thin File",
    desc: "Intelligent estimation for applicants with limited credit history.",
  },
];

function FeaturesSection() {
  return (
    <section className={styles.featuresSection}>
      {/* Section heading */}
      <div className={styles.sectionHeader}>
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className={styles.sectionTitle}
        >
          Powerful Infrastructure
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className={styles.sectionSubtitle}
        >
          Enterprise-grade tools designed for accuracy, transparency, and speed.
        </motion.p>
      </div>

      {/* Feature cards grid */}
      <div className={styles.featuresGrid}>
        {features.map((f, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, delay: i * 0.08 }}
          >
            <ShimmerTiltCard className="h-full">
              <div className={styles.featureCard}>
                <span className={styles.featureIcon}>
                  <f.icon className={styles.featureIconSvg} />
                </span>
                <h3 className={styles.featureTitle}>
                  {f.title}
                </h3>
                <p className={styles.featureDesc}>
                  {f.desc}
                </p>
              </div>
            </ShimmerTiltCard>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* How It Works */
/* ------------------------------------------------------------------ */

const steps = [
  {
    num: "01",
    title: "Submit Application",
    desc: "Send applicant data through the unified API gateway with a single POST request.",
  },
  {
    num: "02",
    title: "AI Analysis",
    desc: "LightGBM scores risk, FAISS finds peers, and SHAP generates explanations in parallel.",
  },
  {
    num: "03",
    title: "Get Decision",
    desc: "Receive a comprehensive credit decision with explainability and peer context in real-time.",
  },
];

function HowItWorksSection() {
  return (
    <section className={styles.howItWorksSection}>
      <div className={styles.sectionHeader}>
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className={styles.sectionTitle}
        >
          How It Works
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className={styles.sectionSubtitle}
        >
          From application to decision in three simple steps.
        </motion.p>
      </div>

      <div className={styles.stepsGrid}>
        {steps.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, delay: i * 0.15 }}
            className={styles.stepWrapper}
          >
            <ShimmerTiltCard className="h-full">
              <div className={styles.stepCard}>
                {/* Numbered circle */}
                <span className={styles.stepNumber}>
                  {step.num}
                </span>
                <h3 className={styles.stepTitle}>
                  {step.title}
                </h3>
                <p className={styles.stepDesc}>
                  {step.desc}
                </p>
              </div>
            </ShimmerTiltCard>

            {/* Connector arrow (hidden on last card and mobile) */}
            {i < steps.length - 1 && (
              <div className={styles.connectorArrow}>
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <path
                    d="M5 12h14m-4-4 4 4-4 4"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* CTA */
/* ------------------------------------------------------------------ */

function CTASection() {
  return (
    <section className={styles.ctaSection}>
      <BackgroundBeams beamColor="#F3CA40" />

      <div className={styles.ctaContent}>
        <TextGenerateEffect
          words="Transform Your Credit Process"
          className="text-4xl font-bold tracking-tight text-neutral-100 md:text-5xl"
        />

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 1 }}
          className={styles.ctaSubtitle}
        >
          Deploy intelligent scoring in minutes. No infrastructure, no training
          data — just predictions.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 1.3 }}
          className={styles.ctaButtons}
        >
          <Link
            href="/dashboard"
            className={styles.ctaButtonPrimary}
          >
            Start Free Trial
          </Link>
          <Link
            href="/docs"
            className={styles.ctaButtonSecondary}
          >
            View API Docs
          </Link>
        </motion.div>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Footer */
/* ------------------------------------------------------------------ */

function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerInner}>
        <div className={styles.footerBrand}>
          <span className={styles.footerLogo}>
            CC
          </span>
          <span className={styles.footerBrandName}>
            CredsCore
          </span>
        </div>
        <span className={styles.footerCopyright}>
          &copy; 2026 CredsCore
        </span>
      </div>
    </footer>
  );
}

/* ------------------------------------------------------------------ */
/* Landing Page (single export) */
/* ------------------------------------------------------------------ */

export function LandingPage() {
  return (
    <div className={styles.page}>
      <Navigation />
      <HeroSection />
      <StatsSection />
      <FeaturesSection />
      <HowItWorksSection />
      <CTASection />
      <Footer />
    </div>
  );
}
