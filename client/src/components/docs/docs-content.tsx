"use client";

import { cn } from "@/lib/utils";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./docs-content.module.scss";

const CODE_EXAMPLE = `// Example: Make a credit risk prediction via API Gateway
const response = await fetch('http://localhost:4000/client-predict', {
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
  'http://localhost:4000/client-predict',
  json={
    'RevolvingUtilizationOfUnsecuredLines': 0.766,
    'age': 45,
    'DebtRatio': 0.803,
    'MonthlyIncome': 9120.0,
    'NumberOfTime30_59DaysPastDueNotWorse': 2,
    'NumberOfOpenCreditLinesAndLoans': 13,
    'NumberOfTimes90DaysLate': 0,
    'NumberRealEstateLoansOrLines': 6,
    'NumberOfTime60_89DaysPastDueNotWorse': 0,
    'NumberOfDependents': 2,
  }
)
result = response.json()
print(result)`;

const ENDPOINTS = [
  { method: "POST", path: "/client-predict", description: "Make a credit risk prediction (routes to Credit Scoring on port 8000)", params: ["RevolvingUtilizationOfUnsecuredLines", "age", "DebtRatio", "MonthlyIncome", "...10 features total"] },
  { method: "POST", path: "/similar-applicants", description: "Find similar past applicants using FAISS (routes to Credit Scoring on port 8000)", params: ["k (optional, default=10)"] },
  { method: "POST", path: "/explain-denial", description: "Explain denial with SHAP and counter-examples (routes to Credit Scoring on port 8000)", params: ["k (optional, default=20)"] },
  { method: "POST", path: "/thin-file-predict", description: "Enhanced prediction for thin-file applicants (routes to Credit Scoring on port 8000)", params: ["k (optional, default=5)"] },
  { method: "POST", path: "/monitor-drift", description: "Monitor model drift via cluster centroids (routes to Credit Scoring on port 8000)", params: ["n_clusters (optional, default=10)"] },
  { method: "POST", path: "/peer-groups", description: "Segment customers into peer groups (routes to Credit Scoring on port 8000)", params: ["n_clusters (optional, default=5)"] },
  { method: "POST", path: "/similar", description: "Check fraud similarity (routes to Fraud Detection on port 8002)", params: ["k (optional, default=10)"] },
  { method: "GET", path: "/fraud-rings", description: "Get detected fraud rings (routes to Fraud Detection on port 8002)", params: [] },
  { method: "POST", path: "/evaluate", description: "Evaluate credit policy decision (routes to Policy on port 8003)", params: ["risk_score", "requested_amount", "monthly_income", "debt_ratio"] },
  { method: "POST", path: "/score", description: "Get combined augmented score (routes to Augmented Scoring on port 8008)", params: ["applicant_id", "features"] },
  { method: "POST", path: "/insights", description: "Get human-readable analysis insights (routes to Augmented Scoring on port 8008)", params: ["applicant_id", "features"] },
  { method: "POST", path: "/enrich", description: "Enrich applicant data with bureau/banking data (routes to Data Enrichment on port 8006)", params: ["client_id", "name", "email", "ssn", "phone", "address"] },
  { method: "POST", path: "/apply", description: "Submit loan application workflow (routes to Orchestrator on port 8005)", params: ["applicant", "requested_amount"] },
  { method: "POST", path: "/synthetic/generate", description: "Generate synthetic test data (routes to Synthetic Data on port 8007)", params: ["num_records", "apply_constraints", "random_seed"] },
];

const MODELS = [
  { icon: "\u{1F333}", title: "LightGBM", desc: "Gradient boosting framework for high-accuracy credit predictions", details: ["Fast training", "Low memory usage", "High accuracy", "Feature importance via SHAP"] },
  { icon: "\u{1F50D}", title: "SHAP", desc: "Explainable AI for feature attribution and denial explanations", details: ["Feature attribution", "Model-agnostic", "Visual explanations", "Regulatory compliance"] },
  { icon: "\u{1F4CA}", title: "FAISS", desc: "Vector similarity search for finding similar applicants and fraud patterns", details: ["Fast nearest neighbor", "Scalable to millions", "Memory efficient", "Used by both Credit & Fraud services"] },
  { icon: "\u{1F9E0}", title: "SNN", desc: "Spiking Neural Network for fraud ring detection", details: ["Graph-based detection", "Unsupervised learning", "Ring pattern recognition", "Adaptive thresholds"] },
  { icon: "\u{1F52C}", title: "Causal Inference", desc: "What-if analysis and counterfactual estimation", details: ["Propensity scoring", "Treatment effect estimation", "Counterfactual scenarios", "Uplift modeling"] },
  { icon: "\u{1F310}", title: "Social Capital", desc: "Network analysis for creditworthiness assessment", details: ["Centrality metrics", "Community detection", "Anomaly detection", "30% weight in augmented scoring"] },
];

const QUICK_START_STEPS = [
  { step: 1, title: "Start All Services", code: "bash scripts/start-all.sh", desc: "Starts all microservices (Credit Scoring, Fraud, Policy, etc.) and the API Gateway on port 4000" },
  { step: 2, title: "Start the Frontend", code: "cd client && npm run dev", desc: "The Next.js dashboard will be available at http://localhost:3000" },
  { step: 3, title: "Verify Health", code: "curl http://localhost:4000/health", desc: "Check that the API Gateway and backend services are running" },
  { step: 4, title: "Make a Prediction", code: "curl -X POST http://localhost:4000/client-predict -H \"Content-Type: application/json\" -d '{...}'", desc: "Send applicant data through the gateway to get a risk prediction" },
];

export { CODE_EXAMPLE, PYTHON_EXAMPLE, ENDPOINTS, MODELS, QUICK_START_STEPS };

export function DocsHeader() {
  return (
    <nav className={styles.docsNav}>
      <div className={styles.docsNavInner}>
        <a href="/" className={styles.docsNavBrand}>
          <div className={styles.docsNavLogo}>
            <span>CC</span>
          </div>
          <span className={styles.docsNavBrandName}>CredsCore</span>
        </a>
        <div className={styles.docsNavLinks}>
          <a href="/" className={styles.docsNavLink}>Home</a>
          <a href="/dashboard" className={styles.docsNavLink}>Dashboard</a>
          <a href="/docs" className={styles.docsNavLinkActive}>Docs</a>
        </div>
      </div>
    </nav>
  );
}

export function DocsSidebar({ sections, activeSection, onSectionChange }: { sections: { id: string; title: string; icon: string }[]; activeSection: string; onSectionChange: (id: string) => void }) {
  return (
    <aside className={styles.sidebar}>
      <nav className={styles.sidebarNav}>
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => onSectionChange(section.id)}
            className={cn(
              activeSection === section.id ? styles.sidebarItemActive : styles.sidebarItem
            )}
          >
            <span>{section.icon}</span>
            <span>{section.title}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}

export function OverviewContent() {
  const stats = [
    { icon: "\u{1F3AF}", title: "99.2% Accuracy", desc: "High-precision predictions" },
    { icon: "\u26A1", title: "< 100ms Response", desc: "Real-time inference" },
    { icon: "\u{1F50D}", title: "Explainable AI", desc: "SHAP-based explanations" },
  ];
  const backendItems = [
    { dotClass: styles.architectureDotPrimary, text: "LightGBM for predictions" },
    { dotClass: styles.architectureDotCyan, text: "SHAP for explanations" },
    { dotClass: styles.architectureDotPurple, text: "FAISS for similarity search" },
    { dotClass: styles.architectureDotPrimary, text: "SNN for fraud ring detection" },
    { dotClass: styles.architectureDotCyan, text: "Causal inference for what-if analysis" },
    { dotClass: styles.architectureDotPurple, text: "Social capital for network scoring" },
  ];
  const frontendItems = [
    { dotClass: styles.architectureDotPrimary, text: "Modern UI with Tailwind CSS v4" },
    { dotClass: styles.architectureDotCyan, text: "Interactive visualizations" },
    { dotClass: styles.architectureDotPurple, text: "Real-time API integration via Gateway" },
  ];
  return (
    <div className={styles.contentSection}>
      <h1 className={styles.pageTitle}>CredsCore Documentation</h1>
      <p className={styles.pageDescription}>CredsCore is an AI-powered credit risk assessment platform that combines LightGBM, SHAP explanations, FAISS vector search, SNN fraud detection, causal inference, and social capital analysis to provide accurate, explainable, and fast credit decisions.</p>

      <div className={styles.overviewStatsGrid}>
        {stats.map((item, i) => (
          <ShimmerBorder key={i} borderRadius="1rem">
            <div className={styles.overviewStatCard}>
              <div className={styles.overviewStatIcon}>{item.icon}</div>
              <h3 className={styles.overviewStatTitle}>{item.title}</h3>
              <p className={styles.overviewStatDesc}>{item.desc}</p>
            </div>
          </ShimmerBorder>
        ))}
      </div>

      <ShimmerBorder borderRadius="1rem">
        <div className={styles.architectureCard}>
          <h2 className={styles.architectureTitle}>Architecture</h2>
          <div className={styles.architectureGrid}>
            <div>
              <h3 className={styles.architectureColumnTitle}>Backend (FastAPI Microservices)</h3>
              <ul className={styles.architectureList}>
                {backendItems.map((item, i) => (
                  <li key={i} className={styles.architectureItem}>
                    <span className={item.dotClass} />
                    <span>{item.text}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className={styles.architectureColumnTitle}>Frontend (Next.js 16)</h3>
              <ul className={styles.architectureList}>
                {frontendItems.map((item, i) => (
                  <li key={i} className={styles.architectureItem}>
                    <span className={item.dotClass} />
                    <span>{item.text}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </ShimmerBorder>
    </div>
  );
}

export function QuickStartContent() {
  return (
    <div className={styles.contentSection}>
      <h1 className={styles.pageTitle}>Quick Start Guide</h1>
      <p className={styles.pageDescription}>Get up and running with CredsCore in minutes. All frontend requests go through the API Gateway at <code className={styles.inlineCode}>localhost:4000</code>.</p>
      <div className={styles.quickStartList}>
        {QUICK_START_STEPS.map((item) => (
          <ShimmerBorder key={item.step} borderRadius="1rem">
            <div className={styles.quickStartCard}>
              <div className={styles.quickStartNumber}>
                {item.step}
              </div>
              <div className={styles.quickStartContent}>
                <h3 className={styles.quickStartTitle}>{item.title}</h3>
                <p className={styles.quickStartDesc}>{item.desc}</p>
                <div className={styles.codeBlock}>
                  <code className={styles.codeBlockText}>{item.code}</code>
                </div>
              </div>
            </div>
          </ShimmerBorder>
        ))}
      </div>
    </div>
  );
}

export function ApiReferenceContent() {
  return (
    <div className={styles.contentSection}>
      <h1 className={styles.pageTitle}>API Reference</h1>
      <p className={styles.pageDescription}>Complete API documentation for all CredsCore endpoints.</p>

      <ShimmerBorder borderRadius="1rem">
        <div className={styles.apiSection}>
          <h2 className={styles.apiSectionTitle}>Base URL</h2>
          <div className={styles.codeBlock}>
            <code className={styles.codeBlockText}>http://localhost:4000</code>
          </div>
          <p className={styles.apiSectionDescription}>All requests go through the API Gateway which routes to the appropriate microservice.</p>
        </div>
      </ShimmerBorder>

      <ShimmerBorder borderRadius="1rem">
        <div className={styles.apiSection}>
          <h2 className={styles.apiSectionTitle}>Gateway Routing</h2>
          <p className={styles.apiSectionDescription}>The gateway proxies requests to the correct backend service based on path:</p>
          <div className={styles.codeBlock}>
            <pre className={styles.codePre}>{`/client-predict, /similar-applicants -> Credit Scoring (8000)
/similar, /fraud-rings -> Fraud Detection (8002)
/evaluate -> Policy (8003)
/apply, /applications -> Orchestrator (8005)
/enrich -> Data Enrichment (8006)
/synthetic/* -> Synthetic Data (8007)
/score, /insights, /combined-score -> Augmented Scoring (8008)`}</pre>
          </div>
        </div>
      </ShimmerBorder>

      <ShimmerBorder borderRadius="1rem">
        <div className={styles.apiSection}>
          <h2 className={styles.apiSectionTitle}>Authentication</h2>
          <p className={styles.apiSectionDescription}>Currently, the API does not require authentication for local development.</p>
          <div className={styles.warningBox}>
            <p className={styles.warningText}>For production deployments, implement proper authentication.</p>
          </div>
        </div>
      </ShimmerBorder>
    </div>
  );
}

export function EndpointsContent() {
  return (
    <div className={styles.contentSection}>
      <h1 className={styles.pageTitle}>API Endpoints</h1>
      <p className={styles.pageDescription}>All available endpoints and their parameters. All requests go through the API Gateway at <code className={styles.inlineCode}>localhost:4000</code>.</p>
      <div className={styles.endpointsList}>
        {ENDPOINTS.map((endpoint, i) => (
          <ShimmerBorder key={i} borderRadius="1rem">
            <div className={styles.endpointCard}>
              <div className={styles.endpointHeader}>
                <span className={cn(
                  endpoint.method === "GET" ? styles.methodBadgeGet : styles.methodBadgePost
                )}>
                  {endpoint.method}
                </span>
                <code className={styles.endpointPath}>{endpoint.path}</code>
              </div>
              <p className={styles.endpointDescription}>{endpoint.description}</p>
              {endpoint.params.length > 0 && (
                <div>
                  <h4 className={styles.paramTitle}>Parameters:</h4>
                  <div className={styles.paramChips}>
                    {endpoint.params.map((param, j) => (
                      <span key={j} className={styles.paramChip}>
                        {param}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </ShimmerBorder>
        ))}
      </div>
    </div>
  );
}

export function ExamplesContent() {
  return (
    <div className={styles.contentSection}>
      <h1 className={styles.pageTitle}>Code Examples</h1>
      <p className={styles.pageDescription}>Copy-paste examples to get started quickly. All requests go through the API Gateway at <code className={styles.inlineCode}>localhost:4000</code>.</p>

      <ShimmerBorder borderRadius="1rem">
        <div className={styles.exampleCard}>
          <h2 className={styles.exampleTitle}>JavaScript / TypeScript</h2>
          <div className={styles.exampleCodeBlock}>
            <pre className={styles.codePre}>{CODE_EXAMPLE}</pre>
          </div>
        </div>
      </ShimmerBorder>

      <ShimmerBorder borderRadius="1rem">
        <div className={styles.exampleCard}>
          <h2 className={styles.exampleTitle}>Python</h2>
          <div className={styles.exampleCodeBlock}>
            <pre className={styles.codePre}>{PYTHON_EXAMPLE}</pre>
          </div>
        </div>
      </ShimmerBorder>
    </div>
  );
}

export function ModelsContent() {
  return (
    <div className={styles.contentSection}>
      <h1 className={styles.pageTitle}>ML Models</h1>
      <p className={styles.pageDescription}>Understanding the models behind CredsCore. The Augmented Scoring service combines ML (60%), Social (30%), and Causal (10%) scores.</p>
      <div className={styles.modelsGrid}>
        {MODELS.map((model, i) => (
          <ShimmerBorder key={i} borderRadius="1rem">
            <div className={styles.modelCard}>
              <div className={styles.modelIcon}>{model.icon}</div>
              <h3 className={styles.modelTitle}>{model.title}</h3>
              <p className={styles.modelDesc}>{model.desc}</p>
              <ul className={styles.modelDetailsList}>
                {model.details.map((detail, j) => (
                  <li key={j} className={styles.modelDetailItem}>
                    <span className={styles.modelDetailDot} />
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>
          </ShimmerBorder>
        ))}
      </div>
    </div>
  );
}
