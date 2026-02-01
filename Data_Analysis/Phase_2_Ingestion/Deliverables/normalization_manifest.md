# Folder and File Normalization

To address inconsistencies in naming conventions across study folders and files, a normalization process has been implemented.

## Directory Structure
The normalized data is stored in `Standardized_Study_Files/`.
Original data remains in `QC Anonymized Study Files/`.

## Canonical Naming Conventions

### Folders
Pattern: `Study_{ID}_Input_Files`
Example: `Study_1_Input_Files`, `Study_20_Input_Files`

### Files
Each study contains exactly 9 standardized files.

| Canonical Name | regex pattern used | Description |
| :--- | :--- | :--- |
| `Study_{ID}_EDC_Metrics.xlsx` | `.*EDC.*Metrics.*` | EDC System Metrics |
| `Study_{ID}_EDRR.xlsx` | `.*EDRR.*` | Compiled EDRR Reports |
| `Study_{ID}_MedDRA.xlsx` | `.*Med.*RA.*` | Global Coding Report (MedDRA) |
| `Study_{ID}_WHODrug.xlsx` | `.*(WHO.*D|WHO.*Drug).*` | Global Coding Report (WHODrug) |
| `Study_{ID}_Inactivated_Records.xlsx` | `.*Inactivated.*` | Inactivated Forms/Folders/Records |
| `Study_{ID}_Lab_Discrepancies.xlsx` | `.*(Missing.*Lab\|Missing.*Range\|Missing.*LNR).*` | Missing Lab Name & Ranges |
| `Study_{ID}_Missing_Pages.xlsx` | `.*Missing.*Page.*` | Global Missing Pages Report |
| `Study_{ID}_Visit_Projection.xlsx` | `.*(Visit.*Projection\|Missing.*Visit).*` | Visit Projection Tracker |
| `Study_{ID}_SAE_Dashboard.xlsx` | `.*SAE.*Dashboard.*` | eSAE Dashboard (DM & Safety) |

## Script
The script used to perform this normalization is located at `normalize_filenames.py`.
It uses regex matching to robustly identify files despite variations in naming (e.g., date formats, typos, extra spaces).

## Execution
The script has already been executed, and the `Standardized_Study_Files` folder is populated.
To re-run:
```bash
python3 normalize_filenames.py --execute
```
