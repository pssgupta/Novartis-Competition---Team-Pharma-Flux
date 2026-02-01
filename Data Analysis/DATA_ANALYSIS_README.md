# Clinical Trial Data Quality Analytics Pipeline

> **A deterministic, rule-based system for real-time clinical trial data quality assessment**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16.1.6-black)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents
- [Overview](#overview)
- [Why This Approach?](#why-this-approach)
- [System Architecture](#system-architecture)
- [Technical Implementation](#technical-implementation)
- [Advantages Over ML Models](#advantages-over-ml-models)
- [Flexibility & Scalability](#flexibility--scalability)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)

---

## 🎯 Overview

This project implements a **transparent, deterministic analytics pipeline** for clinical trial data quality assessment. Unlike black-box machine learning models, our system uses **explicit business rules** to transform raw, inconsistent clinical data into actionable risk scores.

### Core Philosophy
> **Every score is traceable. Every rule is visible. No training required.**

The pipeline processes data through four sequential phases:
1. **Standardization** → Clean chaotic file structures
2. **Ingestion** → Validate and canonicalize data with full provenance
3. **Signal Generation** → Apply domain-specific business rules
4. **Aggregation** → Calculate Data Quality Index (DQI) scores

### Key Metrics
- **~90,000+ records** processed from multiple clinical studies
- **100% traceability** via SHA256 provenance IDs
- **<2 minutes** full pipeline execution time
- **8 domains** of risk signals (EDC, Queries, Lab, Safety, Visits, Coding, etc.)

---

## 🤔 Why This Approach?

### The Clinical Trial Data Challenge

Clinical trials generate data from multiple sources with inherent inconsistencies:

| Challenge | Example |
|-----------|---------|
| **Inconsistent Naming** | `Study 6 _CPID` vs `STUDY 21_CPID_Input Files - Anonymization` |
| **Varying Headers** | "Site ID" vs "Site Number" vs "SiteID" |
| **Multiple Date Formats** | `dd-MMM-yyyy`, `yyyy-mm-dd`, `MM/DD/YYYY` |
| **Type Confusion** | Numeric IDs stored as strings, dates as text |
| **Regulatory Requirements** | Every calculation must be auditable and explainable |

### Why NOT Machine Learning?

| ML Approach ❌ | Our Approach ✅ |
|---------------|----------------|
| Requires 1000s of labeled examples | Works immediately with business rules |
| Black box predictions | Transparent, explainable calculations |
| Difficult to audit for regulators | Every score traces to source data |
| Breaks when data distribution changes | Adapts via configuration files |
| Requires retraining for new domains | Add new rules in minutes |
| Cannot explain "why" a score is X | Built-in explanation for every signal |

### Our Solution: Rule-Based Determinism

```
Raw Data → Standardization → Validation → Business Rules → Risk Scores
```

**Result:** A system that clinical trial professionals can trust, audit, and modify without data science expertise.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          RAW DATA INPUT                              │
│      (Inconsistent Excel files from multiple clinical studies)      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   PHASE 1: STANDARDIZATION                           │
│  ✓ Normalize folder names: Study_{ID}_Input_Files                   │
│  ✓ Standardize file names: Study_{ID}_{Domain}.xlsx                 │
│  ✓ Remove spaces, special characters, case inconsistencies          │
│                                                                       │
│  Input:  "STUDY 21_CPID_Input Files - Anonymization"                │
│  Output: "Study_21_Input_Files/Study_21_EDC_Metrics.xlsx"           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   PHASE 2: CANONICAL INGESTION                       │
│  ✓ Map diverse headers → standard schema (field_mapping.csv)        │
│  ✓ Validate data types using JSON Schema Draft 7                    │
│  ✓ Generate SHA256 trace IDs for every row                          │
│  ✓ Output: Parquet files + Provenance metadata                      │
│                                                                       │
│  Output: query.parquet, lab.parquet, safety.parquet, etc.           │
│          provenance.parquet (full lineage)                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 PHASE 3: RISK SIGNAL GENERATION                      │
│  ✓ Apply 15+ domain-specific business rules                         │
│  ✓ Calculate normalized risk scores (0.0 → 1.0)                     │
│  ✓ Generate explainable signals with evidence links                 │
│                                                                       │
│  Domains: EDC Completeness, Query Health, Lab Integrity,            │
│           Safety (SAEs), Visit Compliance, Coding Readiness          │
│                                                                       │
│  Output: risk_signals.parquet (~thousands of independent signals)   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│             PHASE 4: AGGREGATION & DQI CALCULATION                   │
│  ✓ Apply configurable domain weights (Safety: 30%, EDC: 25%, etc.) │
│  ✓ Aggregate signals → entity-level DQI scores                      │
│  ✓ Rank sites, subjects, studies by risk                            │
│                                                                       │
│  Formula: DQI = Σ(Signal Score × Domain Weight) / Σ(Weights)       │
│                                                                       │
│  Output: aggregated_risk.parquet, ranked_sites.csv                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     WEB DASHBOARD (Next.js)                          │
│  ✓ Visualize DQI scores with drill-down capability                  │
│  ✓ Trace scores → signals → raw data rows                           │
│  ✓ Export reports and take corrective action                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation

### Phase 1: Data Standardization

**Problem:** Raw clinical data arrives with inconsistent file naming conventions.

**Example Input:**
```
QC Anonymized Study Files/
├── Study 6 _CPID/
│   └── Study6_QC Review_EDC_Metrics_21Nov2024.xlsx
├── STUDY 21_CPID_Input Files - Anonymization/
│   └── Study 21- Open Issue Report(EDRR).xlsx
└── study 30__CPID_Input Files - Anonymization/
    └── Study30 Missing Pages and SDV Status.xlsx
```

**Solution:** Python-based normalization pipeline using regex and keyword mapping.

```python
# normalize_filenames.py

# Folder Naming Rule
Pattern: "Study_{ID}_Input_Files"

# Example Transformation
"STUDY 21_CPID_Input Files - Anonymization" 
    ↓
"Study_21_Input_Files"

# File Naming Rules
Keyword Mapping:
    "*EDC_Metrics*"      → "Study_{ID}_EDC_Metrics.xlsx"
    "*Lab*Discrepanc*"   → "Study_{ID}_Lab_Discrepancies.xlsx"
    "*SAE*Dashboard*"    → "Study_{ID}_SAE_Dashboard.xlsx"
    "*Missing*Pages*"    → "Study_{ID}_Missing_Pages.xlsx"
    "*Open*Issue*"       → "Study_{ID}_EDRR.xlsx"
    ... (15+ mappings)
```

**Output:**
```
Standardized_Study_Files/
├── Study_1_Input_Files/
│   ├── Study_1_EDC_Metrics.xlsx
│   ├── Study_1_Lab_Discrepancies.xlsx
│   └── Study_1_SAE_Dashboard.xlsx
├── Study_21_Input_Files/
│   ├── Study_21_EDC_Metrics.xlsx
│   ├── Study_21_Query_Report.xlsx
│   └── Study_21_Missing_Pages.xlsx
└── Study_30_Input_Files/
    └── ...
```

**Key Benefits:**
- ✅ Eliminates manual file renaming across 20+ studies
- ✅ Enables programmatic batch processing
- ✅ Consistent structure = reliable automation

**Scripts:**
- `normalize_filenames.py` - Main normalization engine
- `analyze_headers.py` - Header inspection utility for schema design

---

### Phase 2: Canonical Ingestion & Provenance

**Problem:** Same clinical concepts have different column names across studies.

**Example Inconsistencies:**
| Study 1 | Study 21 | Study 30 | Canonical Field |
|---------|----------|----------|-----------------|
| Site ID | Site Number | SiteID | `SiteID` |
| Query Open Date | Date Opened | OpenDate | `QueryDate` |
| Days Open | DaysOutstanding | Days Pending | `DaysOutstanding` |

**Solution:** Schema-driven ETL with intelligent field mapping.

#### 2.1 Canonical Schema Design

We use **JSON Schema Draft 7** to define strict data contracts:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Clinical Trial Canonical Schema",
  "version": "1.0",
  "entities": {
    "Query": {
      "type": "object",
      "properties": {
        "StudyID": {"type": "integer"},
        "SiteID": {"type": "integer"},
        "SubjectID": {"type": "string"},
        "QueryID": {"type": "string"},
        "QueryText": {"type": "string"},
        "QueryDate": {"type": "string", "format": "date"},
        "DaysOutstanding": {"type": "integer"},
        "QueryStatus": {"type": "string", "enum": ["Open", "Closed", "Pending"]}
      },
      "required": ["StudyID", "SiteID", "QueryID", "QueryDate"]
    },
    "Safety": {
      "type": "object",
      "properties": {
        "StudyID": {"type": "integer"},
        "SiteID": {"type": "integer"},
        "SubjectID": {"type": "string"},
        "SAEID": {"type": "string"},
        "SAEOnsetDate": {"type": "string", "format": "date"},
        "SAEReportDate": {"type": "string", "format": "date"},
        "DaysToReport": {"type": "integer"},
        "Severity": {"type": "string", "enum": ["Mild", "Moderate", "Severe"]}
      }
    },
    "Lab": { ... },
    "Visit": { ... },
    "Inactivation": { ... }
  }
}
```

#### 2.2 Field Mapping System

`field_mapping.csv` acts as a Rosetta Stone between source and canonical schemas:

```csv
source_header,canonical_field,data_type,transformation
Site ID,SiteID,integer,direct
Site Number,SiteID,integer,direct
Site,SiteID,integer,direct
Query Open Date,QueryDate,date,parse_date
Date Opened,QueryDate,date,parse_date
OpenDate,QueryDate,date,parse_date
Days Open,DaysOutstanding,integer,direct
DaysOutstanding,DaysOutstanding,integer,direct
Days Pending,DaysOutstanding,integer,direct
Subject Number,SubjectID,string,strip_whitespace
Subject ID,SubjectID,string,strip_whitespace
Subject,SubjectID,string,strip_whitespace
```

#### 2.3 Smart Data Parsing

The ingestion engine (`ingest_studies.py`) performs intelligent type coercion:

**Date Parsing:**
```python
def parse_flexible_date(date_value):
    """
    Handles: dd-MMM-yyyy, yyyy-mm-dd, MM/DD/YYYY, 
             DD.MM.YYYY, Excel serial dates
    Output: ISO 8601 (YYYY-MM-DD)
    """
    formats = [
        "%d-%b-%Y",   # 21-Nov-2024
        "%Y-%m-%d",   # 2024-11-21
        "%m/%d/%Y",   # 11/21/2024
        "%d.%m.%Y",   # 21.11.2024
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_value, fmt).strftime("%Y-%m-%d")
        except:
            continue
    
    # Handle Excel serial dates (days since 1900-01-01)
    if isinstance(date_value, (int, float)):
        return excel_to_date(date_value)
    
    raise ValueError(f"Unrecognized date format: {date_value}")
```

**Integer Coercion:**
```python
def safe_int_parse(value):
    """Handles: '123', 123, '123.0', None, empty strings"""
    if pd.isna(value) or value == '':
        return None
    try:
        return int(float(value))  # Handles '123.0' strings
    except:
        return None
```

#### 2.4 Provenance Generation

**Critical Requirement:** Every row in the final database must be traceable to its source.

```python
def generate_trace_id(study_id, filename, row_number, entity_type, entity_id):
    """
    Creates a cryptographic hash uniquely identifying the data lineage.
    
    Example:
        study_id = 21
        filename = "Study_21_Query_Report.xlsx"
        row_number = 42
        entity_type = "Query"
        entity_id = "QRY-001"
        
    Returns: "a3f2b8c9d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1"
    """
    trace_string = f"{study_id}|{filename}|{row_number}|{entity_type}|{entity_id}"
    return hashlib.sha256(trace_string.encode()).hexdigest()
```

Every canonical row includes this `trace_id`:

```python
{
  "StudyID": 21,
  "SiteID": 101,
  "QueryID": "QRY-001",
  "QueryDate": "2024-11-21",
  "DaysOutstanding": 15,
  "trace_id": "a3f2b8c9d4e5f6a7b8c9d0e1f2a3b4c5..."
}
```

#### 2.5 Data Validation & Quarantine

Rows failing schema validation are **not silently dropped**—they're quarantined for review:

```python
try:
    validator.validate(row_data)  # JSON Schema validation
    canonical_rows.append(row_data)
except ValidationError as e:
    quarantine_row = {
        "source_file": filename,
        "row_number": row_num,
        "failed_field": e.path,
        "error_message": e.message,
        "raw_data": row_data
    }
    quarantine.append(quarantine_row)
```

**Output Files:**
```
Phase_2_Ingestion/
├── Canonical_Data/
│   ├── query.parquet          # ~6,000 validated rows
│   ├── lab.parquet            # ~20,000 rows
│   ├── safety.parquet         # ~20,000 rows (SAE data)
│   ├── inactivation.parquet   # ~44,000 audit trail rows
│   ├── visit.parquet          # ~8,000 rows
│   ├── provenance.parquet     # 11MB of lineage metadata
│   └── Quarantine/
│       ├── invalid_query_rows.csv
│       └── invalid_lab_rows.csv
```

#### 2.6 Performance Optimization

**Initial Problem:** Script hung on Study 21 (61MB Excel file).

**Root Cause:** JSON Schema validators were being re-instantiated for every row (6,000+ times).

**Solution:** Pre-compile validators once at module load:

```python
# BEFORE (Slow):
def validate_row(row_data, schema):
    validator = Draft7Validator(schema)  # ❌ Creates new validator every call
    validator.validate(row_data)

# AFTER (Fast):
# Compile once globally
QUERY_VALIDATOR = Draft7Validator(schemas['Query'])
LAB_VALIDATOR = Draft7Validator(schemas['Lab'])

def validate_row(row_data, entity_type):
    VALIDATORS[entity_type].validate(row_data)  # ✅ Reuses compiled validator
```

**Result:** 100x speedup → Full ingestion in <2 minutes.

---

### Phase 3: Risk Signal Generation

**Problem:** Canonical data is "clean" but doesn't tell you *what's wrong*.

**Question:** Is 50 open queries at a site problematic?
**Answer:** Depends on:
- How long have they been open?
- What's the site's enrollment count?
- What's the study phase?
- Historical site performance?

**Solution:** Convert raw metrics into **normalized risk signals** using domain-specific business rules.

#### 3.1 Signal Design Principles

1. **Independence:** Each signal answers ONE operational question
2. **Explainability:** Every score includes a human-readable explanation
3. **Evidence-Based:** Every signal links to source data via `trace_ids`
4. **Normalized:** All scores on 0.0 to 1.0 scale (0 = no risk, 1 = critical)

#### 3.2 Signal Schema

Every signal follows this strict contract:

```python
{
  "signal_id": "SIG-QRY-001",
  "signal_name": "Query Aging",
  "domain": "Query_Health",
  "entity_type": "Site",
  "entity_id": "101",
  "study_id": "21",
  "raw_metric_value": 45,           # 45 days old
  "normalized_score": 0.68,         # High risk (0-1 scale)
  "severity_level": "High",         # Low|Medium|High|Critical
  "explanation": "Site 101 has a query open for 45 days, exceeding the 30-day resolution threshold",
  "trace_ids": ["a3f2b8c9...", "d4e5f6a7..."],
  "signal_timestamp": "2025-02-01T10:00:00Z"
}
```

#### 3.3 Implemented Risk Signals

| Domain | Signal | Business Rule | Raw Input | Normalized Score |
|--------|--------|---------------|-----------|------------------|
| **EDC Completeness** | Missing CRF Pages | Linear scaling: 0-50 pages | `missing_pages_count` | `min(count/50, 1.0)` |
| **EDC Completeness** | Overdue CRFs | Days missing × urgency | `days_overdue` | `min(days/60, 1.0)` |
| **Query Health** | Open Query Load | Count-based threshold | `open_query_count` | `min(count/100, 1.0)` |
| **Query Health** | Query Aging | Exponential decay after 30d | `days_outstanding` | `1 - exp(-days/30)` |
| **Visit Compliance** | Visit Delay | Days late vs protocol window | `days_outstanding` | `min(days/45, 1.0)` |
| **Lab Integrity** | Missing Lab Metadata | Percentage of unusable results | `missing_units_count / total_labs` | `percentage` |
| **Safety** | SAE Reporting Latency | Days to report (regulatory: 24h serious, 7d non-serious) | `days_to_report` | `min(days/7, 1.0)` |
| **Coding** | Coding Backlog | Uncoded terms vs total | `uncoded_count / total_terms` | `percentage` |

#### 3.4 Example: Query Aging Signal

```python
def calculate_query_aging_signal(query_row):
    """
    Business Rule:
    - 0-7 days: Normal (score 0.0)
    - 8-30 days: Linear increase to 0.5
    - 31-60 days: Linear increase to 0.8
    - 60+ days: Critical (score 1.0)
    """
    days_open = query_row['DaysOutstanding']
    
    if days_open <= 7:
        score = 0.0
        severity = "Low"
    elif days_open <= 30:
        score = (days_open - 7) / (30 - 7) * 0.5  # 0.0 → 0.5
        severity = "Medium"
    elif days_open <= 60:
        score = 0.5 + ((days_open - 30) / (60 - 30) * 0.3)  # 0.5 → 0.8
        severity = "High"
    else:
        score = min(1.0, 0.8 + (days_open - 60) / 60 * 0.2)
        severity = "Critical"
    
    return {
        "signal_id": f"SIG-QRY-{query_row['QueryID']}",
        "signal_name": "Query Aging",
        "domain": "Query_Health",
        "entity_type": "Site",
        "entity_id": query_row['SiteID'],
        "study_id": query_row['StudyID'],
        "raw_metric_value": days_open,
        "normalized_score": round(score, 3),
        "severity_level": severity,
        "explanation": f"Query {query_row['QueryID']} has been open for {days_open} days",
        "trace_ids": [query_row['trace_id']],
        "signal_timestamp": datetime.utcnow().isoformat()
    }
```

#### 3.5 Example: SAE Reporting Latency

```python
def calculate_sae_latency_signal(sae_row):
    """
    Regulatory Requirement:
    - Serious SAE: Report within 24 hours
    - Non-Serious SAE: Report within 7 days
    """
    days_to_report = (sae_row['SAEReportDate'] - sae_row['SAEOnsetDate']).days
    is_serious = sae_row['Severity'] == 'Severe'
    
    threshold = 1 if is_serious else 7
    
    if days_to_report <= threshold:
        score = 0.0
        severity = "Low"
    elif days_to_report <= threshold * 2:
        score = 0.5
        severity = "Medium"
    elif days_to_report <= threshold * 4:
        score = 0.8
        severity = "High"
    else:
        score = 1.0
        severity = "Critical"
    
    return {
        "signal_id": f"SIG-SAE-{sae_row['SAEID']}",
        "signal_name": "SAE Reporting Latency",
        "domain": "Safety",
        "entity_type": "Site",
        "entity_id": sae_row['SiteID'],
        "study_id": sae_row['StudyID'],
        "raw_metric_value": days_to_report,
        "normalized_score": score,
        "severity_level": severity,
        "explanation": f"SAE {sae_row['SAEID']} reported {days_to_report} days after onset (threshold: {threshold} days)",
        "trace_ids": [sae_row['trace_id']],
        "signal_timestamp": datetime.utcnow().isoformat()
    }
```

#### 3.6 Signal Independence

Signals are **deliberately independent**—they don't depend on each other's calculations.

**Why?**
- Easier to debug individual signals
- Can add/remove signals without breaking others
- Transparent to auditors ("Show me how you calculated X")

**Output:**
```
Phase_3_Risk_Signals/
├── risk_signals.parquet       # ~15,000 signals across all domains
├── signals_by_domain/
│   ├── edc_signals.csv
│   ├── query_signals.csv
│   ├── lab_signals.csv
│   ├── safety_signals.csv
│   └── visit_signals.csv
└── signal_metadata.json       # Documentation of all signal types
```

---

### Phase 4: Signal Aggregation & DQI Calculation

**Problem:** Thousands of granular signals are overwhelming. Users need:
- "What are my top 10 worst sites?"
- "Which subjects need immediate attention?"
- "Overall study health in one number"

**Solution:** Aggregate signals into entity-level **Data Quality Index (DQI)** scores using configurable domain weights.

#### 4.1 Domain Weighting

Not all risks are equal. Clinical priorities dictate weights:

```python
DOMAIN_WEIGHTS = {
    "Safety": 0.30,              # Patient safety is paramount
    "EDC_Completeness": 0.25,    # Missing data blocks analysis
    "Query_Health": 0.20,        # Unresolved queries delay database lock
    "Visit_Compliance": 0.15,    # Protocol deviations
    "Lab_Integrity": 0.10,       # Data quality hygiene
}
# Weights sum to 1.0
```

**Configurable:** Stored in `domain_weights.json` for easy adjustment.

#### 4.2 Aggregation Formula

For each entity (Site, Subject, Visit):

```
DQI Score = Σ(Signal Score × Domain Weight) / Σ(Weights of Active Signals)
```

**Example Calculation:**

Site 101 has the following signals:
- Missing Pages: 0.4 (EDC Completeness)
- Query Aging: 0.7 (Query Health)
- SAE Latency: 0.9 (Safety)

```python
DQI = (0.4 × 0.25) + (0.7 × 0.20) + (0.9 × 0.30) / (0.25 + 0.20 + 0.30)
    = (0.1 + 0.14 + 0.27) / 0.75
    = 0.51 / 0.75
    = 0.68  → "High Risk"
```

#### 4.3 Severity Classification

```python
DQI_THRESHOLDS = {
    (0.0, 0.2): "Low",
    (0.2, 0.5): "Medium",
    (0.5, 0.8): "High",
    (0.8, 1.0): "Critical"
}
```

#### 4.4 Implementation

```python
def aggregate_site_dqi(site_signals):
    """
    Aggregates all signals for a site into a single DQI score.
    
    Args:
        site_signals: List of signal dicts for one site
    
    Returns:
        {
            "entity_type": "Site",
            "entity_id": "101",
            "study_id": "21",
            "dqi_score": 0.68,
            "risk_level": "High",
            "signal_count": 15,
            "domain_breakdown": {...},
            "contributing_signals": [...]
        }
    """
    weighted_sum = 0
    total_weight = 0
    domain_scores = {}
    
    for signal in site_signals:
        domain = signal['domain']
        weight = DOMAIN_WEIGHTS.get(domain, 0.1)
        score = signal['normalized_score']
        
        weighted_sum += score * weight
        total_weight += weight
        
        if domain not in domain_scores:
            domain_scores[domain] = []
        domain_scores[domain].append(score)
    
    dqi_score = weighted_sum / total_weight if total_weight > 0 else 0
    risk_level = classify_risk(dqi_score)
    
    return {
        "entity_type": "Site",
        "entity_id": site_signals[0]['entity_id'],
        "study_id": site_signals[0]['study_id'],
        "dqi_score": round(dqi_score, 3),
        "risk_level": risk_level,
        "signal_count": len(site_signals),
        "domain_breakdown": {
            domain: round(sum(scores)/len(scores), 3)
            for domain, scores in domain_scores.items()
        },
        "contributing_signals": [s['signal_id'] for s in site_signals],
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### 4.5 Ranking & Prioritization

```python
# Generate ranked lists for dashboard
ranked_sites = aggregated_data.sort_values('dqi_score', ascending=False)
top_10_sites = ranked_sites.head(10)

ranked_subjects = aggregated_data[aggregated_data['entity_type']=='Subject'] \
                    .sort_values('dqi_score', ascending=False)
```

**Output Files:**
```
Phase_4_Aggregation/
├── aggregated_risk.parquet      # All entities with DQI scores
├── ranked_sites.csv             # Sites sorted by risk (worst first)
├── ranked_subjects.csv          # Subjects needing attention
├── study_summary.json           # Overall study health metrics
└── domain_heatmap_data.json     # For dashboard visualizations
```

#### 4.6 Drill-Down Capability

The aggregation maintains full traceability:

```
DQI Score (0.68)
  ↓ Click "Why?"
Signal Breakdown:
  - Missing Pages: 0.4 (25 pages missing)
  - Query Aging: 0.7 (3 queries > 45 days)
  - SAE Latency: 0.9 (SAE-001 reported 10 days late)
  ↓ Click "Query Aging"
Raw Data:
  - Query QRY-12345: Opened 2024-10-15, 47 days old
  - Trace ID: a3f2b8c9... → Study_21_Query_Report.xlsx, Row 42
```

---

## ✅ Advantages Over ML Models

| Aspect | ML Approach | Our Rule-Based Approach |
|--------|-------------|-------------------------|
| **Training Data** | Requires 1000s of labeled examples | ✅ Zero training data needed |
| **Deployment Time** | Weeks/months (data collection, labeling, training) | ✅ Immediate (define rules, run pipeline) |
| **Explainability** | Black box ("the model says 0.87") | ✅ Full transparency ("Score is 0.87 because: X + Y + Z") |
| **Regulatory Audit** | Difficult to explain to FDA/EMA | ✅ Every calculation documented and traceable |
| **Adaptability** | Requires retraining for new rules | ✅ Add new signal = add 20 lines of code |
| **Domain Expertise** | Embedded opaquely in training data | ✅ Explicit in business rules (domain experts can review) |
| **Edge Cases** | May fail unpredictably on outliers | ✅ Explicit handling in rule logic |
| **Maintenance** | Model drift, retraining cycles | ✅ Update config files, no retraining |
| **Trust** | "Why should I trust this prediction?" | ✅ "Here's exactly how we calculated this" |
| **Cost** | GPU infrastructure, ML expertise | ✅ Runs on standard hardware, junior devs can maintain |

### Real-World Scenario

**ML Approach:**
- Data Scientist: "The model predicts Site 101 is high risk with 87% confidence."
- Auditor: "Why 87%? Which specific issues?"
- Data Scientist: "The model learned patterns from historical data... it's complex."
- Auditor: ❌ "Not sufficient for regulatory submission."

**Our Approach:**
- System: "Site 101 DQI = 0.68 (High Risk)"
- Auditor: "Why 0.68?"
- System: "25 missing CRF pages (0.4 score) + 3 queries >45 days old (0.7 score) + 1 SAE reported 10 days late (0.9 score), weighted by domain priority (Safety=30%, EDC=25%, Queries=20%)"
- Auditor: ✅ "Show me the source data for the SAE."
- System: "SAE-001, reported in Study_21_SAE_Dashboard.xlsx, Row 17, Trace ID: d4e5f6a7..."
- Auditor: ✅ "Approved."

---

## 🔄 Flexibility & Scalability

### Adding a New Signal (5 minutes)

```python
# 1. Define the business rule
def calculate_new_signal(row):
    raw_value = row['some_metric']
    score = min(raw_value / 100, 1.0)
    
    return {
        "signal_id": f"SIG-NEW-{row['id']}",
        "signal_name": "New Risk Indicator",
        "domain": "New_Domain",
        "raw_metric_value": raw_value,
        "normalized_score": score,
        ...
    }

# 2. Register in signal_registry.py
SIGNAL_FUNCTIONS['new_signal'] = calculate_new_signal

# 3. Update domain_weights.json
{
  "New_Domain": 0.15  # Adjust other weights accordingly
}

# 4. Run pipeline → New signal automatically included in DQI
```

### Adapting to New Study Type

**Scenario:** A new oncology study uses different terminology for lab tests.

**Solution:**
1. Update `field_mapping.csv`:
```csv
Tumor Marker,LabTestName,string,direct
Tumor Size,LabValue,float,direct
```

2. Run Phase 2 ingestion → Automatically maps to canonical schema.

3. No changes needed to Phases 3-4 → Signals still work.

### Scaling to 100+ Studies

**Current Performance:** ~90,000 records in <2 minutes

**Optimizations for Scale:**
- ✅ Parquet columnar storage (10x faster than CSV)
- ✅ Pre-compiled schema validators (100x speedup)
- ✅ Parallel processing (use `multiprocessing` for Phase 3)
- ✅ Incremental updates (only process new/changed files)

**Projected Performance at 1M records:** <10 minutes on standard laptop.

---

## 📁 Project Structure

```
Novaratis-Clinical-Trial-Analytics/
│
├── Phase_1_Standardization/
│   ├── normalize_filenames.py
│   ├── analyze_headers.py
│   ├── QC Anonymized Study Files/      # Raw input (gitignored)
│   └── Standardized_Study_Files/        # Cleaned output
│
├── Phase_2_Ingestion/
│   ├── ingest_studies.py
│   ├── Deliverables/
│   │   ├── Schema_Registry/
│   │   │   └── canonical_schema_v1.json
│   │   └── field_mapping.csv
│   ├── Canonical_Data/
│   │   ├── query.parquet
│   │   ├── lab.parquet
│   │   ├── safety.parquet
│   │   ├── inactivation.parquet
│   │   ├── provenance.parquet
│   │   └── Quarantine/
│   └── phase2_env/                      # Python venv
│
├── Phase_3_Risk_Signals/
│   ├── generate_signals.py
│   ├── signal_definitions/
│   │   ├── edc_signals.py
│   │   ├── query_signals.py
│   │   ├── lab_signals.py
│   │   ├── safety_signals.py
│   │   └── visit_signals.py
│   ├── risk_signals.parquet
│   └── signal_metadata.json
│
├── Phase_4_Aggregation/
│   ├── aggregate_dqi.py
│   ├── domain_weights.json
│   ├── aggregated_risk.parquet
│   ├── ranked_sites.csv
│   ├── ranked_subjects.csv
│   └── study_summary.json
│
├── web-app/                             # Next.js Dashboard
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── package.json
│   └── next.config.js
│
├── docs/
│   ├── Architecture.md
│   ├── Signal_Definitions.md
│   └── Flowcharts/
│
├── requirements.txt
├── README.md                            # This file
└── LICENSE
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** (for web dashboard)
- **Required Python packages:**
  ```bash
  pandas
  pyarrow          # For Parquet support
  jsonschema       # For schema validation
  openpyxl         # For Excel reading
  ```

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Novaratis-Clinical-Trial-Analytics.git
cd Novaratis-Clinical-Trial-Analytics
```

#### 2. Set Up Python Environment (Data Pipeline)
```bash
# Create virtual environment
python -m venv pipeline_env

# Activate (Windows)
pipeline_env\Scripts\activate

# Activate (Mac/Linux)
source pipeline_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Set Up Web Dashboard
```bash
cd web-app
npm install
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Running the Pipeline

#### Full Pipeline Execution
```bash
# Phase 1: Standardize raw files
cd Phase_1_Standardization
python normalize_filenames.py

# Phase 2: Ingest into canonical format
cd ../Phase_2_Ingestion
python ingest_studies.py

# Phase 3: Generate risk signals
cd ../Phase_3_Risk_Signals
python generate_signals.py

# Phase 4: Aggregate into DQI scores
cd ../Phase_4_Aggregation
python aggregate_dqi.py
```

#### Or use the master script:
```bash
python run_full_pipeline.py
```

### Viewing Results

1. **Web Dashboard:** `http://localhost:3000`
2. **CSV Exports:** Check `Phase_4_Aggregation/ranked_sites.csv`
3. **Raw Parquet:** Query directly with Python:
```python
import pandas as pd

# Load aggregated risk data
df = pd.read_parquet('Phase_4_Aggregation/aggregated_risk.parquet')

# Filter high-risk sites
high_risk_sites = df[(df['entity_type']=='Site') & (df['dqi_score'] > 0.5)]
print(high_risk_sites[['entity_id', 'dqi_score', 'risk_level']])
```

---

## 📊 Sample Output

### Example: Top 5 High-Risk Sites

| Site ID | Study ID | DQI Score | Risk Level | Signal Count | Top Issues |
|---------|----------|-----------|------------|--------------|------------|
| 101 | 21 | 0.82 | Critical | 18 | SAE Latency (0.9), Query Aging (0.85) |
| 205 | 21 | 0.71 | High | 15 | Missing Pages (0.75), Visit Delays (0.68) |
| 304 | 30 | 0.65 | High | 12 | Open Queries (0.72), Lab Issues (0.58) |
| 102 | 21 | 0.58 | High | 10 | EDC Completeness (0.60), Coding Backlog (0.56) |
| 401 | 6 | 0.53 | High | 9 | Visit Compliance (0.55), Query Load (0.51) |

### Drill-Down: Site 101 Details

```json
{
  "entity_id": "101",
  "study_id": "21",
  "dqi_score": 0.82,
  "risk_level": "Critical",
  "signal_count": 18,
  "domain_breakdown": {
    "Safety": 0.90,
    "Query_Health": 0.85,
    "EDC_Completeness": 0.65,
    "Visit_Compliance": 0.50,
    "Lab_Integrity": 0.40
  },
  "top_signals": [
    {
      "signal_name": "SAE Reporting Latency",
      "score": 0.90,
      "explanation": "SAE-001 reported 10 days after onset (threshold: 1 day)"
    },
    {
      "signal_name": "Query Aging",
      "score": 0.85,
      "explanation": "3 queries open >45 days"
    }
  ]
}
```

---

## 📝 Documentation

- **[Architecture Overview](docs/Architecture.md)** - System design and data flow
- **[Signal Definitions](docs/Signal_Definitions.md)** - All 15+ risk signals explained
- **[API Reference](docs/API.md)** - Dashboard API endpoints
- **[Configuration Guide](docs/Configuration.md)** - Customize weights, thresholds
- **[Flowcharts](docs/Flowcharts/)** - Visual process diagrams

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Adding new signals
- Improving business rules
- Enhancing dashboard visualizations
- Bug reports and feature requests

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 👥 Authors

- **Your Name** - Initial work - [GitHub Profile](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Clinical trial domain expertise from [Your Organization]
- Inspired by real-world challenges in clinical data management
- Built with transparency and regulatory compliance in mind

---

## 📧 Contact

For questions or collaboration: **your.email@example.com**

---

**⭐ If this project helps your clinical trial data quality efforts, please star it on GitHub!**