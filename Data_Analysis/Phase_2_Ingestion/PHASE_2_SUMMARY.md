# Phase 2: Canonical Ingestion & Provenance

## 1. Executive Summary
Phase 2 focused on transforming the flat, standardized Excel files from Phase 1 into a relational, typed, and fully traceable canonical data store. We designed a JSON Schema to govern the data structure and built a robust ETL (Extract, Transform, Load) pipeline to ingest the data, validate it row-by-row, and generate provenance metadata.

## 2. Methodology

### 2.1 Schema Design
We defined a central schema (`canonical_schema_v1.json`) using JSON Schema Draft 7.
*   **Entities Definition:**
    *   **Dimensional:** `Study`, `Site`, `Subject`
    *   **Transactional:** `Visit`, `Form`, `Query`, `Lab`, `Coding`, `Safety`, `Inactivation`
*   **Validation Rules:** strict typing (Integers for counts, ISO8601 for dates) to ensure data quality at the gate.

### 2.2 Ingestion Engine (`ingest_studies.py`)
A custom Python ETL engine was built to handle the specific logic of clinical trial data.

*   **Mapping Strategy:** Used `field_mapping.csv` to map diverse source headers (e.g., "Site ID", "Site Number") to canonical fields (`SiteID`).
*   **Smart Parsing:**
    *   **Dates:** Auto-detection of multiple date formats (`dd-MMM-yyyy`, `yyyy-mm-dd`, etc.) normalized to `YYYY-MM-DD`.
    *   **Integers:** Robust handling of types for count fields (e.g., `DaysOutstanding`).
*   **Performance Optimization:** Implement pre-compiled `Draft7Validator` instances to handle large files (e.g., Study 21, 60MB+) efficiently without re-initializing schemas per row.

### 2.3 Provenance & Traceability
A core requirement was full traceability. We implemented a hashing mechanism:
*   **Trace ID:** `SHA256(StudyID + FileName + RowNumber + EntityType + EntityID)`
*   This ID is attached to every single row in the canonical output and stored in a central `provenance.parquet` file. This allows any record in the final DB to be traced back to the exact row in the specific Excel file it came from.

## 3. Architecture & Folder Structure
The Phase 2 workspace is self-contained:

```text
Phase_2_Ingestion/
├── Canonical_Data/             # The "Gold" layer output
│   ├── [entity].parquet        # Optimized columnar storage (e.g., query.parquet)
│   ├── [entity].csv            # Human-readable mirrors
│   ├── provenance.parquet      # The Source-of-Truth for lineage
│   └── Quarantine/             # Rows that failed Schema Validation
├── Deliverables/
│   ├── Schema_Registry/        # JSON Schemas
│   └── field_mapping.csv       # Source-to-Target Maps
├── ingest_studies.py           # The execution engine
└── phase2_env/                 # Isolated Python virtual environment
```

## 4. Artifacts & Deliverables
| Artifact | Type | Stats (Approx) | Description |
| :--- | :--- | :--- | :--- |
| `query.parquet` | Data | ~6,000 rows | Standardized Queries/Discrepancies. |
| `lab.parquet` | Data | ~20,000 rows | Lab normal range issues. |
| `safety.parquet` | Data | ~20,000 rows | SAE (Serious Adverse Event) data. |
| `inactivation.parquet` | Data | ~44,000 rows | Audit trail of deleted/inactivated records. |
| `provenance.parquet` | Metadata | ~11MB | Full lineage linking every row to source. |

## 5. Performance Improvements
*   **Issue:** Initial scripts "hung" on Study 21 (61MB) due to inefficient schema validator initialization.
*   **Fix:** Refactored `ingest_studies.py` to compile validators once globally.
*   **Result:** Reduced processing time 100x, enabling full dataset ingestion in under 2 minutes.

## 6. Outcome
*   **Status:** Complete
*   **Verification:** `Canonical_Data` populated with Parquet/CSV files. `Quarantine` folder captures invalid rows.
*   **Next Steps:** These Parquet files are now ready to be loaded into a Data Warehouse (Snowflake, BigQuery) or analyzed directly using PySpark/Pandas.
