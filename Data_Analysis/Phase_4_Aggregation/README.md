# Phase 4: Signal Aggregation, Weighting & DQI

## Objective
Convert thousands of granular risk signals into a small number of prioritized, interpretable scores (Data Quality Index - DQI) that tell users where to act first.

## Design Principles
1.  **Prioritization:** Aggregate granular signals into actionable scores.
2.  **Explainability:** DQI = Computed weighted sum of known problems. No black box.
3.  **Configurability:** Domain weights are defined in an external config file.
4.  **Consistency:** Higher Score = Higher Risk (0.0 - 1.0).

## Methodology

### 1. Weights
We apply domain-level weights to prioritize critical clinical operations areas.

| Domain | Weight | Rationale |
| :--- | :--- | :--- |
| **Safety** | 0.30 | Patient safety is paramount (SAEs). |
| **EDC Completeness** | 0.25 | Missing data blocks analysis. |
| **Query Health** | 0.20 | Unresolved queries delay DB lock. |
| **Visit Compliance** | 0.15 | Protocol deviations. |
| **Lab Integrity** | 0.10 | Data quality hygiene. |
| **Coding Readiness** | 0.20 | (Alternative high weight if near lock). |

*(Note: Weights normalize to sum to 1.0 in calculation)*

### 2. Aggregation Logic
For each entity (Site, Subject):
$$ \text{DQI Score} = \frac{\sum (\text{Signal Score} \times \text{Risk Factor} \times \text{Domain Weight})}{\sum \text{Weights of Active Signals}} $$

*Simple Summation is chosen for MVP to ensure transparency.*

### 3. Severity Classification
| DQI Score | Risk Level |
| :--- | :--- |
| 0.0 - 0.2 | Low |
| 0.2 - 0.5 | Medium |
| 0.5 - 0.8 | High |
| > 0.8 | Critical |

## Outputs
1.  **`aggregated_risk.csv/parquet`**: The master table of entities with their DQI scores.
2.  **`ranked_sites.csv`**: Top sites requiring attention.
3.  **`ranked_subjects.csv`**: Top subjects requiring attention.

## Use Case
This data feeds the Web App dashboard, allowing:
*   "Show me the Top 10 worst sites."
*   "Why is Site 101 Red?" -> Drill down into specific signals.
