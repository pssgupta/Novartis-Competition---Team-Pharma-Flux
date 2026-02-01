# Data Normalization Rules

## 1. Domain Vocabularies
To ensure cross-study comparability, specific columns must be mapped to controlled vocabularies.

### Query Status
*   **Source Values:** "Open", "Answered", "Closed", "Candidate", "Cancelled" (and case variations)
*   **Target Domain:** `['Open', 'Answered', 'Closed', 'Cancelled']`
*   **Rule:** 
    *   Map "Candidate" -> "Open" (or specific status if defined)
    *   Map "Auto-Closed" -> "Closed"
    *   Convert to Title Case.

### Country Codes
*   **Source Values:** "USA", "United States", "DEU", "Germany", etc.
*   **Target Domain:** ISO 3166-1 alpha-3 code (e.g., USA, DEU, GBR).
*   **Rule:** Use a lookup table to standardise full names to 3-letter codes.

### Subject Status
*   **Source Values:** "Screened", "Screen Failed", "Enrolled", "Randomized", "Completed", "Discontinued"
*   **Target Domain:** Canonical Enums defined in Schema.

## 2. Temporal Normalization (Time Model)

### Date Formats
All dates must be converted to **ISO 8601 (YYYY-MM-DD)**.
*   **Input Formats Detected:**
    *   `DD-MMM-YYYY` (e.g., 14-Nov-2025)
    *   `DD MMM YYYY` (e.g., 14 NOV 2025)
*   **Rule:** Parse string using locale-aware parser and format as `%Y-%m-%d`.

### Timezones
*   Study timestamps are often local to the site or UTC.
*   **Rule:** Unless explicitly stated with offset, assume Site Local Time. Ideally, convert all system timestamps (e.g., Audit Time, Query Log) to **UTC**.

## 3. Numeric & Unit Normalization

### Lab Units
(If Lab Results were present in these specific files)
*   **Rule:** Convert all units to SI units where applicable.
*   **Examples:** `mg/dL` -> `mmol/L` (Glucose).

### Days Calculations
*   Fields like `DaysOutstanding`, `DaysMissing`.
*   **Rule:** Ensure these are Integers. If "N/A" or blank, treat as `null` (not 0, to distinguish missing vs zero).

## 4. Text Normalization
*   **Trim Whitespace:** Remove leading/trailing spaces from `SiteID`, `SubjectID`.
*   **Column Mapping:** Use the `field_mapping.csv` to handle "Site Number" vs "SiteNumber" to `SiteID`.
