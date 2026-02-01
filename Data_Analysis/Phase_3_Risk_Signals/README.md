# Phase 3: Risk Signal Generation

## Objective
Convert trusted canonical operational data into independent, explainable, domain-specific risk signals that quantify data quality and operational bottlenecks.

## Design Principles
1.  **One Signal = One Operational Question**
2.  **Independence:** Signals do not depend on each other.
3.  **Explainability:** Every score is traceable to raw evidence.
4.  **Evidence-Based:** Every signal row links to `trace_ids` from Phase 2.

## Signal Schema
Every signal follows this contract:
*   `signal_id`: Unique identifier (e.g., SIG-001)
*   `signal_name`: Human readable name
*   `domain`: Operational domain (EDC, Safety, etc.)
*   `entity_type`: Site, Subject, or Visit
*   `entity_id`: The ID of the entity
*   `study_id`: Context
*   `raw_metric_value`: The actual count/ratio/days
*   `normalized_score`: 0.0 to 1.0 (Risk Scale)
*   `severity_level`: Low, Medium, High, Critical
*   `explanation`: Text description
*   `trace_ids`: List of provenance IDs
*   `signal_timestamp`: When this signal was computed

## Domains Implemented
### Domain 1: EDC Data Completeness
*   **Missing Pages** (Count/Risk of missing forms)
*   **Overdue CRFs** (Based on days missing)

### Domain 2: Visit Compliance
*   **Visit Delay** (Days outstanding)

### Domain 3: Query Health
*   **Open Query Load** (Count of open queries)
*   **Query Aging** (Long-running queries)

### Domain 4: Lab Data
*   **Missing Lab Metadata** (Uninterpretable results)

### Domain 5: Safety & Coding
*   **SAE Latency** (Review time)
*   **Coding Backlog** (Uncoded terms)
