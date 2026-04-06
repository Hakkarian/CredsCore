import styles from "./docs-api-reference.module.scss";

export function ApiReferenceContent() {
  return (
    <div className={styles.docsSection}>
      <h1 className={styles.docsTitle}>API Reference</h1>
      <p className={styles.docsSubtitle}>Complete API documentation for all CredsCore endpoints.</p>
      <div className={styles.docsCard}>
        <h2 className={styles.docsHeading}>Base URL</h2>
        <code className={styles.docsCodeBlock}>http://localhost:8000</code>
      </div>
      <div className={styles.docsCard}>
        <h2 className={styles.docsHeading}>Authentication</h2>
        <p className={styles.docsText}>Currently, the API does not require authentication for local development.</p>
        <div className={styles.docsNote}>
          <p>For production deployments, implement proper authentication.</p>
        </div>
      </div>
    </div>
  );
}