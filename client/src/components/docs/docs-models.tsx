import cn from "classnames";
import { TreeDeciduous, Search, Database, Target } from "lucide-react";
import styles from "./docs-models.module.scss";

const MODELS = [
  { icon: TreeDeciduous, title: "LightGBM", desc: "Gradient boosting framework for high-accuracy predictions", details: ["Fast training", "Low memory usage", "High accuracy"] },
  { icon: Search, title: "SHAP", desc: "Explainable AI for feature importance", details: ["Feature attribution", "Model-agnostic", "Visual explanations"] },
  { icon: Database, title: "FAISS", desc: "Vector similarity search for finding similar applicants", details: ["Fast nearest neighbor", "Scalable", "Memory efficient"] },
  { icon: Target, title: "StandardScaler", desc: "Feature normalization for consistent predictions", details: ["Zero mean", "Unit variance", "Prevents bias"] },
];

export function ModelsContent() {
  return (
    <div className={styles.docsSection}>
      <h1 className={styles.docsTitle}>ML Models</h1>
      <p className={styles.docsSubtitle}>Understanding the models behind CredsCore.</p>
      <div className={cn(styles.docsCardGrid, styles.cols2)}>
        {MODELS.map((model, i) => {
          const Icon = model.icon;
          return (
            <div key={i} className={styles.docsCard}>
              <div className={styles.docsCardIcon}><Icon className={styles.docsCardIconSvg} /></div>
              <h3 className={styles.docsCardTitle}>{model.title}</h3>
              <p className={styles.docsCardDesc}>{model.desc}</p>
              <ul className={styles.docsCardList}>
                {model.details.map((detail, j) => (
                  <li key={j} className={styles.docsCardListItem}>
                    <span className={cn(styles.docsCardDot, styles["dot-primary"])} />
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}