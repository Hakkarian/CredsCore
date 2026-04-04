"use client";

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

const ENDPOINTS = [
  { method: "POST", path: "/predict", description: "Make a credit risk prediction", params: ["RevolvingUtilizationOfUnsecuredLines", "age", "DebtRatio", "MonthlyIncome"] },
  { method: "POST", path: "/similar-applicants", description: "Find similar past applicants using FAISS", params: ["k (optional, default=10)"] },
  { method: "POST", path: "/explain-denial", description: "Explain denial with SHAP and counter-examples", params: ["k (optional, default=20)"] },
  { method: "POST", path: "/thin-file-predict", description: "Enhanced prediction for thin-file applicants", params: ["k (optional, default=5)"] },
  { method: "POST", path: "/monitor-drift", description: "Monitor model drift via cluster centroids", params: ["n_clusters (optional, default=10)"] },
  { method: "POST", path: "/peer-groups", description: "Segment customers into peer groups", params: ["n_clusters (optional, default=5)"] },
];

const MODELS = [
  { icon: "🌳", title: "LightGBM", desc: "Gradient boosting framework for high-accuracy predictions", details: ["Fast training", "Low memory usage", "High accuracy"] },
  { icon: "🔍", title: "SHAP", desc: "Explainable AI for feature importance", details: ["Feature attribution", "Model-agnostic", "Visual explanations"] },
  { icon: "📊", title: "FAISS", desc: "Vector similarity search for finding similar applicants", details: ["Fast nearest neighbor", "Scalable", "Memory efficient"] },
  { icon: "🎯", title: "StandardScaler", desc: "Feature normalization for consistent predictions", details: ["Zero mean", "Unit variance", "Prevents bias"] },
];

const QUICK_START_STEPS = [
  { step: 1, title: "Start the Server", code: "cd server && python main.py", desc: "The API will be available at http://localhost:8000" },
  { step: 2, title: "Verify Health", code: "curl http://localhost:8000/health", desc: "Check that the model and FAISS index are loaded" },
  { step: 3, title: "Make a Prediction", code: "curl -X POST http://localhost:8000/predict -H \"Content-Type: application/json\" -d '{...}'", desc: "Send applicant data to get a risk prediction" },
];

export { CODE_EXAMPLE, PYTHON_EXAMPLE, ENDPOINTS, MODELS, QUICK_START_STEPS };

export function DocsHeader() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-dark">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <a href="/" className="flex items-center space-x-3">
          <div className="w-10 h-10 gradient-primary rounded-xl flex items-center justify-center shadow-lg"><span className="text-white font-bold text-lg">CC</span></div>
          <span className="font-display font-bold text-xl text-white">CredsCore</span>
        </a>
        <div className="flex items-center space-x-6">
          <a href="/" className="text-gray-300 hover:text-white transition-colors">Home</a>
          <a href="/dashboard" className="text-gray-300 hover:text-white transition-colors">Dashboard</a>
          <a href="/docs" className="text-white font-semibold">Docs</a>
        </div>
      </div>
    </nav>
  );
}

export function DocsSidebar({ sections, activeSection, onSectionChange }: { sections: { id: string; title: string; icon: string }[]; activeSection: string; onSectionChange: (id: string) => void }) {
  return (
    <aside className="fixed left-0 top-24 w-64 h-[calc(100vh-6rem)] p-6 border-r border-card-border overflow-y-auto">
      <nav className="space-y-2">
        {sections.map((section) => (
          <button key={section.id} onClick={() => onSectionChange(section.id)} className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-300 ${activeSection === section.id ? "bg-primary/20 text-white font-semibold shadow-lg" : "text-gray-400 hover:bg-white/5 hover:text-white"}`}>
            <span className="text-xl">{section.icon}</span><span>{section.title}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}

export function OverviewContent() {
  const stats = [{ icon: "🎯", title: "99.2% Accuracy", desc: "High-precision predictions" }, { icon: "⚡", title: "< 100ms Response", desc: "Real-time inference" }, { icon: "🔍", title: "Explainable AI", desc: "SHAP-based explanations" }];
  const backendItems = [{ color: "bg-primary", text: "LightGBM for predictions" }, { color: "bg-accent-cyan", text: "SHAP for explanations" }, { color: "bg-accent-lavender", text: "FAISS for similarity search" }];
  const frontendItems = [{ color: "bg-primary", text: "Modern UI with Tailwind CSS" }, { color: "bg-accent-cyan", text: "Interactive visualizations" }, { color: "bg-accent-lavender", text: "Real-time API integration" }];
  return (
    <div className="animate-fade-in">
      <h1 className="font-display text-4xl font-bold text-white mb-6">CredsCore Documentation</h1>
      <p className="text-lg text-gray-400 mb-8 max-w-3xl">CredsCore is an AI-powered credit risk assessment platform that combines LightGBM, SHAP explanations, and FAISS vector search to provide accurate, explainable, and fast credit decisions.</p>
      <div className="grid md:grid-cols-3 gap-6 mb-12">
        {stats.map((item, i) => (<div key={i} className="card"><div className="text-3xl mb-3">{item.icon}</div><h3 className="font-semibold text-white mb-1">{item.title}</h3><p className="text-sm text-gray-400">{item.desc}</p></div>))}
      </div>
      <div className="card">
        <h2 className="font-display text-2xl font-bold text-white mb-4">Architecture</h2>
        <div className="grid md:grid-cols-2 gap-8">
          <div><h3 className="font-semibold text-white mb-3">Backend (FastAPI)</h3><ul className="space-y-2 text-gray-400">{backendItems.map((item, i) => (<li key={i} className="flex items-center space-x-2"><span className={`w-2 h-2 ${item.color} rounded-full`} /><span>{item.text}</span></li>))}</ul></div>
          <div><h3 className="font-semibold text-white mb-3">Frontend (Next.js)</h3><ul className="space-y-2 text-gray-400">{frontendItems.map((item, i) => (<li key={i} className="flex items-center space-x-2"><span className={`w-2 h-2 ${item.color} rounded-full`} /><span>{item.text}</span></li>))}</ul></div>
        </div>
      </div>
    </div>
  );
}

export function QuickStartContent() {
  return (
    <div className="animate-fade-in">
      <h1 className="font-display text-4xl font-bold text-white mb-6">Quick Start Guide</h1>
      <p className="text-lg text-gray-400 mb-8 max-w-3xl">Get up and running with CredsCore in minutes.</p>
      <div className="space-y-6">
        {QUICK_START_STEPS.map((item) => (
          <div key={item.step} className="card">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 gradient-primary rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg">{item.step}</div>
              <div className="flex-1"><h3 className="font-display text-xl font-bold text-white mb-2">{item.title}</h3><p className="text-gray-400 mb-4">{item.desc}</p><div className="bg-card-bg rounded-xl p-4 font-mono text-sm text-white overflow-x-auto">{item.code}</div></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ApiReferenceContent() {
  return (
    <div className="animate-fade-in">
      <h1 className="font-display text-4xl font-bold text-white mb-6">API Reference</h1>
      <p className="text-lg text-gray-400 mb-8 max-w-3xl">Complete API documentation for all CredsCore endpoints.</p>
      <div className="card mb-8"><h2 className="font-display text-2xl font-bold text-white mb-4">Base URL</h2><div className="bg-card-bg rounded-xl p-4 font-mono text-white">http://localhost:8000</div></div>
      <div className="card"><h2 className="font-display text-2xl font-bold text-white mb-4">Authentication</h2><p className="text-gray-400 mb-4">Currently, the API does not require authentication for local development.</p><div className="bg-accent-gold/10 border border-accent-gold/30 rounded-xl p-4"><p className="text-white font-medium">For production deployments, implement proper authentication.</p></div></div>
    </div>
  );
}

export function EndpointsContent() {
  return (
    <div className="animate-fade-in">
      <h1 className="font-display text-4xl font-bold text-white mb-6">API Endpoints</h1>
      <p className="text-lg text-gray-400 mb-8 max-w-3xl">All available endpoints and their parameters.</p>
      <div className="space-y-4">
        {ENDPOINTS.map((endpoint, i) => (
          <div key={i} className="card">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3"><span className="px-3 py-1 bg-green-500/20 text-green-400 text-sm font-semibold rounded-lg">{endpoint.method}</span><code className="font-mono text-white font-semibold">{endpoint.path}</code></div>
            </div>
            <p className="text-gray-400 mb-4">{endpoint.description}</p>
            <div><h4 className="font-semibold text-white text-sm mb-2">Parameters:</h4><div className="flex flex-wrap gap-2">{endpoint.params.map((param, j) => (<span key={j} className="px-3 py-1 bg-primary/20 text-white text-sm rounded-lg">{param}</span>))}</div></div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ExamplesContent() {
  return (
    <div className="animate-fade-in">
      <h1 className="font-display text-4xl font-bold text-white mb-6">Code Examples</h1>
      <p className="text-lg text-gray-400 mb-8 max-w-3xl">Copy-paste examples to get started quickly.</p>
      <div className="card"><h2 className="font-display text-2xl font-bold text-white mb-4">JavaScript / TypeScript</h2><div className="bg-card-bg rounded-xl p-6 font-mono text-sm text-white overflow-x-auto"><pre className="whitespace-pre-wrap">{CODE_EXAMPLE}</pre></div></div>
      <div className="card mt-6"><h2 className="font-display text-2xl font-bold text-white mb-4">Python</h2><div className="bg-card-bg rounded-xl p-6 font-mono text-sm text-white overflow-x-auto"><pre>{PYTHON_EXAMPLE}</pre></div></div>
    </div>
  );
}

export function ModelsContent() {
  return (
    <div className="animate-fade-in">
      <h1 className="font-display text-4xl font-bold text-white mb-6">ML Models</h1>
      <p className="text-lg text-gray-400 mb-8 max-w-3xl">Understanding the models behind CredsCore.</p>
      <div className="grid md:grid-cols-2 gap-6">
        {MODELS.map((model, i) => (
          <div key={i} className="card">
            <div className="text-4xl mb-4">{model.icon}</div>
            <h3 className="font-display text-xl font-bold text-white mb-2">{model.title}</h3>
            <p className="text-gray-400 mb-4">{model.desc}</p>
            <ul className="space-y-2">{model.details.map((detail, j) => (<li key={j} className="flex items-center space-x-2 text-sm text-gray-400"><span className="w-1.5 h-1.5 bg-primary rounded-full" /><span>{detail}</span></li>))}</ul>
          </div>
        ))}
      </div>
    </div>
  );
}