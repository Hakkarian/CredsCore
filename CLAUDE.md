# CLAUDE.md

Credit risk prediction system: FastAPI microservices + Next.js 16 frontend.

## Quick Start

```bash
bash scripts/start-all.sh   # all services
bash scripts/kill-ports.sh  # stop all
cd client && npm run dev    # frontend (port 3000)
```

## Service Map

| Service | Port | Key Endpoints |
|---------|------|---------------|
| Credit Scoring | 8001 | `/client-predict`, `/similar-applicants`, `/explain-denial`, `/peer-groups`, `/monitor-drift`, `/thin-file-predict` |
| Fraud Detection | 8002 | `/similar`, `/fraud-rings` |
| Policy | 8003 | `/policies`, `/evaluate/*` |
| Orchestrator | 8005 | `/apply`, `/applications/*` |
| Data Enrichment | 8006 | `/enrich` |
| Synthetic Data | 8007 | `/generate` |
| Augmented Scoring | 8008 | `/score`, `/insights`, `/agents/analyze`, `/agents/report/{id}` |
| Social Capital | 8009 | `/calculate`, `/network-analysis` |
| API Gateway | 4000 | Proxies all services (path-based routing) |
| Client | 3000 | Next.js 16 dashboard |

## Gateway Routing

All frontend calls go through `localhost:4000`. Path prefix determines target:

- `/client-predict`, `/similar-applicants`, `/peer-groups`, `/monitor-drift` → Credit Scoring (8001)
- `/similar`, `/fraud-rings` → Fraud Detection (8002)
- `/evaluate` → Policy (8003)
- `/apply`, `/applications` → Orchestrator (8005)
- `/enrich` → Enrichment (8006)
- `/synthetic/*` → Synthetic Data (8007)
- `/score`, `/combined`, `/combined-score`, `/predict-enhanced` → Augmented Scoring (8008)

Unmatched paths fall through to Credit Scoring (8001) as default.

**Note:** Augmented Scoring client in `api.ts` calls `localhost:8008` directly (bypasses gateway) for `/insights`, `/agents/analyze`, `/agents/report`.

## Credit Scoring Input (10 features)

```json
{"RevolvingUtilizationOfUnsecuredLines": 0.766, "age": 45, "NumberOfTime30_59DaysPastDueNotWorse": 2, "DebtRatio": 0.803, "MonthlyIncome": 9120, "NumberOfOpenCreditLinesAndLoans": 13, "NumberOfTimes90DaysLate": 0, "NumberRealEstateLoansOrLines": 6, "NumberOfTime60_89DaysPastDueNotWorse": 0, "NumberOfDependents": 2}
```

## Architecture

- **Frontend**: Next.js 16 App Router, Tailwind v4 (tokens only), SCSS modules, `client/src/lib/api.ts`
- **SCSS**: Design tokens in `client/src/styles/_variables.scss`, 31 `.module.scss` files for components
- **Tailwind**: Used only for `@theme` tokens in `globals.css` and Aceternity UI primitives in `client/src/components/ui/`
- **Backend**: FastAPI with shared package at `services/shared/credscore_shared/`
- **ML Stack**: LightGBM (credit), FAISS (similarity), SNN (fraud), causal + social inference
- **Augmented Scoring**: 60% ML + 10% Causal + 30% Social combined score
  - `inference_engine.py`: `calculate_combined_score()` — ML base, causal adds `(1-propensity)*0.1`, social adds `risk_indicators*0.3`
  - Causal: propensity score from `CausalEngine._calculate_causal(features)` — high propensity = low risk
  - Social: `SocialNetworkAnalyzer.calculate_social_capital(entity_id, features)` — features param required, else falls back to hardcoded defaults

## Known Pitfalls

- **numpy serialization**: `peers.py` (peer-groups) must convert all numpy types to native Python (`int()`, `float()`, `bool()`) before returning dicts — FastAPI's `jsonable_encoder` can't handle `np.bool_`, `np.float64`, etc.
- **numpy randomness**: Use `np.random.default_rng(seed)` not deprecated `np.random.seed()`. The latter mutates global state; the former isolates per-call so unseeded calls produce different data.
- **Social capital features**: Always pass `features` to `calculate_social_capital(entity_id, features)`. Without it, the 30% social weight uses hardcoded defaults (util=0.5, debt=0.3, income=5000) making combined scores insensitive to input.
- **Synthetic data quality metrics**: Must be computed from actual generated data distributions, not hardcoded constants. See `calculate_quality_metrics()` in `services/synthetic-data/app/main.py`.

## Critical Files

| Component | Location |
|-----------|----------|
| Gateway routes | `services/api_gateway/main.py` |
| Frontend API client | `client/src/lib/api.ts` |
| Frontend types | `client/src/lib/types.ts` |
| Dashboard | `client/src/app/dashboard/page.tsx` |
| Groups panel | `client/src/components/dashboard/groups-panel.tsx` |
| Insights panel | `client/src/components/insights/insights-panel.tsx` |
| Agents panel | `client/src/components/agentic/agentic-panel.tsx` |
| Credit service | `services/credit_scoring/app/main.py` |
| Peer groups | `services/credit_scoring/app/peers.py` |
| Augmented scoring engine | `services/augmented_scoring/app/inference_engine.py` |
| Synthetic engine | `services/synthetic-data/app/simple_engine.py` |
| React Query hooks | `client/src/hooks/use-credit-api.ts` |

## Conversation Archives

- [Tailwind to SCSS Migration](docs/conversations/tailwind-to-scss-migration.md) — Complete conversation summary (2026-05-04)

## Environment

```bash
NEXT_PUBLIC_API_URL=http://localhost:4000
CREDIT_SCORING_URL=http://localhost:8001
FRAUD_DETECTION_URL=http://localhost:8002
AUGMENTED_SCORING_URL=http://localhost:8008
SYNTHETIC_DATA_URL=http://localhost:8007
```
