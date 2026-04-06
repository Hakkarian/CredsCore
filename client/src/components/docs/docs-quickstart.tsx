import styles from "./docs-quickstart.module.scss";

const QUICK_START_STEPS = [
  { step: 1, title: "Start the Server", code: "cd server && python main.py", desc: "The API will be available at http://localhost:8000" },
  { step: 2, title: "Verify Health", code: "curl http://localhost:8000/health", desc: "Check that the model and FAISS index are loaded" },
  { step: 3, title: "Make a Prediction", code: "curl -X POST http://localhost:8000/predict -H \"Content-Type: application/json\" -d '{...}'", desc: "Send applicant data to get a risk prediction" },
];

export function QuickStartContent() {
  return (
    <div className={styles.docsSection}>
      <h1 className={styles.docsTitle}>Quick Start Guide</h1>
      <p className={styles.docsSubtitle}>Get up and running with CredsCore in minutes.</p>
      <div className={styles.docsCardGrid}>
        {QUICK_START_STEPS.map((item) => (
          <div key={item.step} className={styles.docsQuickStep}>
            <div className={styles.stepContent}>
              <div className={styles.stepNumber}>{item.step}</div>
              <div>
                <h3 className={styles.stepTitle}>{item.title}</h3>
                <p className={styles.stepDesc}>{item.desc}</p>
                <div className={styles.stepCode}>{item.code}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}