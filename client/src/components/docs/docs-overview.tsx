import cn from "classnames";
import { Target, Zap, Search } from "lucide-react";
import styles from "./docs-overview.module.scss";

const STATS = [
  { icon: Target, title: "99.2% Accuracy", desc: "High-precision predictions" },
  { icon: Zap, title: "< 100ms Response", desc: "Real-time inference" },
  { icon: Search, title: "Explainable AI", desc: "SHAP-based explanations" },
];

const BACKEND_ITEMS = [
  { color: "primary" as const, text: "LightGBM for predictions" },
  { color: "cyan" as const, text: "SHAP for explanations" },
  { color: "lavender" as const, text: "FAISS for similarity search" },
];

const FRONTEND_ITEMS = [
  { color: "primary" as const, text: "Modern UI with Tailwind CSS" },
  { color: "cyan" as const, text: "Interactive visualizations" },
  { color: "lavender" as const, text: "Real-time API integration" },
];

export function OverviewContent() {
  return (
    <div className={styles.docsSection}>
      <h1 className={styles.docsTitle}>CredsCore Documentation</h1>
      <p className={styles.docsSubtitle}>CredsCore is an AI-powered credit risk assessment platform that combines LightGBM, SHAP explanations, and FAISS vector search to provide accurate, explainable, and fast credit decisions.</p>
      <div className={styles.docsCardGrid}>
        {STATS.map((item, i) => {
          const Icon = item.icon;
          return (
            <div key={i} className={styles.docsCard}>
              <div className={styles.docsCardIcon}><Icon className={styles.docsCardIconSvg} /></div>
              <h3 className={styles.docsCardTitle}>{item.title}</h3>
              <p className={styles.docsCardDesc}>{item.desc}</p>
            </div>
          );
        })}
      </div>
      <div className={styles.docsCard}>
        <h2 className={styles.docsHeading}>Architecture</h2>
        <div className={cn(styles.docsCardGrid, styles.cols2)}>
          <div>
            <h3 className={styles.docsListTitle}>Backend (FastAPI)</h3>
            <ul className={styles.docsCardList}>
              {BACKEND_ITEMS.map((item, i) => (
                <li key={i} className={styles.docsCardListItem}>
                  <span className={cn(styles.docsCardDot, styles[`dot-${item.color}`])} />
                  <span>{item.text}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className={styles.docsListTitle}>Frontend (Next.js)</h3>
            <ul className={styles.docsCardList}>
              {FRONTEND_ITEMS.map((item, i) => (
                <li key={i} className={styles.docsCardListItem}>
                  <span className={cn(styles.docsCardDot, styles[`dot-${item.color}`])} />
                  <span>{item.text}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}