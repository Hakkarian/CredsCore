export const CODE_EXAMPLE = `// Example: Make a prediction
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

export const PYTHON_EXAMPLE = `import requests

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

export const ENDPOINTS = [
  { method: "POST", path: "/predict", description: "Make a credit risk prediction", params: ["RevolvingUtilizationOfUnsecuredLines", "age", "DebtRatio", "MonthlyIncome"] },
  { method: "POST", path: "/similar-applicants", description: "Find similar past applicants using FAISS", params: ["k (optional, default=10)"] },
  { method: "POST", path: "/explain-denial", description: "Explain denial with SHAP and counter-examples", params: ["k (optional, default=20)"] },
  { method: "POST", path: "/thin-file-predict", description: "Enhanced prediction for thin-file applicants", params: ["k (optional, default=5)"] },
  { method: "POST", path: "/monitor-drift", description: "Monitor model drift via cluster centroids", params: ["n_clusters (optional, default=10)"] },
  { method: "POST", path: "/peer-groups", description: "Segment customers into peer groups", params: ["n_clusters (optional, default=5)"] },
];

export const MODELS = [
  { icon: "🌳", title: "LightGBM", desc: "Gradient boosting framework for high-accuracy predictions", details: ["Fast training", "Low memory usage", "High accuracy"] },
  { icon: "🔍", title: "SHAP", desc: "Explainable AI for feature importance", details: ["Feature attribution", "Model-agnostic", "Visual explanations"] },
  { icon: "📊", title: "FAISS", desc: "Vector similarity search for finding similar applicants", details: ["Fast nearest neighbor", "Scalable", "Memory efficient"] },
  { icon: "🎯", title: "StandardScaler", desc: "Feature normalization for consistent predictions", details: ["Zero mean", "Unit variance", "Prevents bias"] },
];

export const QUICK_START_STEPS = [
  { step: 1, title: "Start the Server", code: "cd server && python main.py", desc: "The API will be available at http://localhost:8000" },
  { step: 2, title: "Verify Health", code: "curl http://localhost:8000/health", desc: "Check that the model and FAISS index are loaded" },
  { step: 3, title: "Make a Prediction", code: "curl -X POST http://localhost:8000/predict -H \"Content-Type: application/json\" -d '{...}'", desc: "Send applicant data to get a risk prediction" },
];