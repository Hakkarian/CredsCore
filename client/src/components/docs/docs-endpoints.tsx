import styles from "./docs-endpoints.module.scss";

const ENDPOINTS = [
  { method: "POST", path: "/predict", description: "Make a credit risk prediction", params: ["RevolvingUtilizationOfUnsecuredLines", "age", "DebtRatio", "MonthlyIncome"] },
  { method: "POST", path: "/similar-applicants", description: "Find similar past applicants using FAISS", params: ["k (optional, default=10)"] },
  { method: "POST", path: "/explain-denial", description: "Explain denial with SHAP and counter-examples", params: ["k (optional, default=20)"] },
  { method: "POST", path: "/thin-file-predict", description: "Enhanced prediction for thin-file applicants", params: ["k (optional, default=5)"] },
  { method: "POST", path: "/monitor-drift", description: "Monitor model drift via cluster centroids", params: ["n_clusters (optional, default=10)"] },
  { method: "POST", path: "/peer-groups", description: "Segment customers into peer groups", params: ["n_clusters (optional, default=5)"] },
];

export function EndpointsContent() {
  return (
    <div className={styles.docsSection}>
      <h1 className={styles.docsTitle}>API Endpoints</h1>
      <p className={styles.docsSubtitle}>All available endpoints and their parameters.</p>
      <div className={styles.docsCardGrid}>
        {ENDPOINTS.map((endpoint, i) => (
          <div key={i} className={styles.docsEndpointCard}>
            <div className={styles.docsEndpointHeader}>
              <span className={styles.docsEndpointMethod}>{endpoint.method}</span>
              <code className={styles.docsEndpointPath}>{endpoint.path}</code>
            </div>
            <p className={styles.docsEndpointDesc}>{endpoint.description}</p>
            <div>
              <h4 className={styles.docsListTitle}>Parameters:</h4>
              <div className={styles.docsEndpointParams}>
                {endpoint.params.map((param, j) => (
                  <span key={j} className={styles.docsEndpointParam}>{param}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}