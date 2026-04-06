import styles from "./docs-examples.module.scss";

const CODE_EXAMPLE = `// Example: Make a prediction
const response = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    RevolvingUtilizationOfUnsecuredLines: 0.766,
    age: 45,
    NumberOfTime30_59DaysPastDueNotWorse: 2,
    DebtRatio: 0.803,
    MonthlyIncome: 9120.0,
    NumberOfOpenCreditLinesAndLoans: 13,
    NumberOfTimes90DaysLate: 0,
    NumberRealEstateLoansOrLines: 6,
    NumberOfTime60_89DaysPastDueNotWorse: 0,
    NumberOfDependents: 2
  })
});
const result = await response.json();
console.log(result);`;

const PYTHON_EXAMPLE = `import requests

response = requests.post(
    'http://localhost:8000/predict',
    json={
        'RevolvingUtilizationOfUnsecuredLines': 0.766,
        'age': 45, 'DebtRatio': 0.803,
        'MonthlyIncome': 9120.0,
    }
)
result = response.json()
print(result)`;

export function ExamplesContent() {
  return (
    <div className={styles.docsSection}>
      <h1 className={styles.docsTitle}>Code Examples</h1>
      <p className={styles.docsSubtitle}>Copy-paste examples to get started quickly.</p>
      <div className={styles.docsCard}>
        <h2 className={styles.docsHeading}>JavaScript / TypeScript</h2>
        <pre className={styles.docsCodeBlock}>{CODE_EXAMPLE}</pre>
      </div>
      <div className={styles.docsCard}>
        <h2 className={styles.docsHeading}>Python</h2>
        <pre className={styles.docsCodeBlock}>{PYTHON_EXAMPLE}</pre>
      </div>
    </div>
  );
}