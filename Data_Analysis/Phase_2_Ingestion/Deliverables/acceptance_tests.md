# Acceptance Test Cases for Canonical Schema

## Test Case 1: Schema Validation
**Objective:** Ensure generated JSON adheres to `canonical_schema_v1.json`.
*   **Input:** Transformed record: `{"StudyID": "Study 1", "SiteID": "1001", "VisitDate": "2025-11-14"}`
*   **Expected Result:** Pass schema validation.
*   **Failure Condition:** `VisitDate` is "14-Nov-2025" (Fail format), `SiteID` is missing (Fail required if mandatory).

## Test Case 2: Date Normalization
**Objective:** Verify disparate date formats are unified.
*   **Input 1:** Study 1 Metrics -> Visit Date: `14 NOV 2025`
*   **Input 2:** Study 10 Metrics -> Visit Date: `14-Nov-2025`
*   **Expected Result (Both):** `2025-11-14`

## Test Case 3: Column Mapping Variation
**Objective:** Verify different column names map to same Canonical Field.
*   **Input Method 1:** File `Study 1...Missing_Pages...`, Col `Site Number`
*   **Input Method 2:** File `Study 10...Missing_Pages...`, Col `SiteNumber`
*   **Expected Result:** Both map to `Site.SiteID`.

## Test Case 4: Subject ID Consistency
**Objective:** Ensure Subject IDs are strings and trimmed.
*   **Input:** `" 1001-001 "`
*   **Expected Result:** `"1001-001"`

## Test Case 5: Enum Constraint
**Objective:** Verify Query Status normalization.
*   **Input:** "candidate" (lowercase)
*   **Expected Result:** "Open" (Mapped per business rule) or "Candidate" (Title case if allowed).

## Validation Script Concept (Python)
```python
import json
import jsonschema
from jsonschema import validate

# Load Schema
with open('Schema_Registry/canonical_schema_v1.json') as s:
    schema = json.load(s)

# Sample Data
data = {
    "StudyID": "Study 1",
    "ProtocolID": "PROT-001", 
    "Phase": "III"
}

try:
    validate(instance=data, schema=schema['definitions']['Study'])
    print("Validation successful")
except jsonschema.exceptions.ValidationError as err:
    print("Validation failed:", err)
```
