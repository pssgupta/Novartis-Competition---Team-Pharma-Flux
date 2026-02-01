import os
import pandas as pd
import json
import hashlib
import uuid
import datetime
import argparse
import logging
from pathlib import Path
from jsonschema import Draft7Validator, ValidationError

# Configuration
BASE_DIR = Path("/Users/mypro16/Desktop/Novaratis/Data for problem Statement 1")
SOURCE_DIR = BASE_DIR / "Phase_1_Standardization/Standardized_Study_Files"
CANONICAL_DIR = BASE_DIR / "Phase_2_Ingestion/Canonical_Data"
QUARANTINE_DIR = CANONICAL_DIR / "Quarantine"
SCHEMA_PATH = BASE_DIR / "Phase_2_Ingestion/Deliverables/Schema_Registry/canonical_schema_v1.json"
MAPPING_PATH = BASE_DIR / "Phase_2_Ingestion/Deliverables/field_mapping.csv"

# Ensure directories exist
os.makedirs(CANONICAL_DIR, exist_ok=True)
os.makedirs(QUARANTINE_DIR, exist_ok=True)

# Global Schema
try:
    with open(SCHEMA_PATH, 'r') as f:
        CANONICAL_SCHEMA = json.load(f)
except Exception as e:
    print(f"CRITICAL: Could not load schema from {SCHEMA_PATH}")
    raise e

# Pre-compile validators for speed
VALIDATORS = {}
for entity_name, entity_def in CANONICAL_SCHEMA.get('definitions', {}).items():
    VALIDATORS[entity_name] = Draft7Validator(entity_def)

# Logging Setup
logging.basicConfig(
    filename=BASE_DIR / 'Phase_2_Ingestion/phase2_ingestion.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

class ProvenanceTracker:
    def __init__(self):
        self.rows = []

    def add_trace(self, study_id, source_file, source_row, entity_type, entity_id):
        raw_str = f"{study_id}{source_file}{source_row}{entity_type}{entity_id}"
        trace_id = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()
        
        self.rows.append({
            'trace_id': trace_id,
            'study_id': study_id,
            'source_file': source_file,
            'source_row_number': source_row,
            'canonical_entity': entity_type,
            'entity_id': str(entity_id),
            'ingestion_timestamp': datetime.datetime.now().isoformat()
        })
        return trace_id

    def save(self):
        if not self.rows:
            return
        df = pd.DataFrame(self.rows)
        # Append mode if file exists (optional, but overwriting for this phase)
        try:
            df.to_parquet(CANONICAL_DIR / "provenance.parquet", index=False)
            df.to_csv(CANONICAL_DIR / "provenance.csv", index=False)
        except Exception as e:
            logging.error(f"Failed to save provenance: {e}")

class CanonicalStore:
    def __init__(self):
        self.data = {
            "Study": [],
            "Site": [],
            "Subject": [],
            "Visit": [],
            "Form": [],
            "Query": [],
            "Lab": [],  # LabEvent
            "Coding": [], # CodingEvent
            "Safety": [], # SAEEvent
            "Inactivation": [] # InactivationEvent
        }
        self.seen_ids = {
            "Study": set(),
            "Site": set(),
            "Subject": set()
        }

    def add_entity(self, entity_type, data, trace_id):
        # Attach trace_id
        data['trace_id'] = trace_id
        
        # Deduplication for dimensional entities (Study, Site, Subject)
        if entity_type in ["Study", "Site", "Subject"]:
            # Create a unique key for dedupe
            key_field = f"{entity_type}ID"
            obj_id = data.get(key_field)
            if obj_id:
                if obj_id in self.seen_ids[entity_type]:
                    return # Skip duplicate
                self.seen_ids[entity_type].add(obj_id)
        
        self.data[entity_type].append(data)

    def save_all(self):
        print("\nSaving canonical tables...")
        for entity_type, rows in self.data.items():
            if not rows:
                continue
            df = pd.DataFrame(rows)
            # Enforce schema types (basic)
            dest_file_parquet = CANONICAL_DIR / f"{entity_type.lower()}.parquet"
            dest_file_csv = CANONICAL_DIR / f"{entity_type.lower()}.csv"
            
            try:
                df.to_parquet(dest_file_parquet, index=False)
                df.to_csv(dest_file_csv, index=False)
                logging.info(f"Saved {len(rows)} rows to {dest_file_parquet}")
            except Exception as e:
                logging.error(f"Failed to save {entity_type}: {e}")

class IngestionEngine:
    def __init__(self):
        self.provenance = ProvenanceTracker()
        self.store = CanonicalStore()
        
    def normalize_date(self, date_str):
        if pd.isna(date_str):
            return None
        # Try multiple formats
        for fmt in ('%Y-%m-%d', '%d-%b-%Y', '%d %b %Y', '%d-%m-%Y'):
            try:
                dt = pd.to_datetime(date_str, format=fmt, errors='coerce')
                if not pd.isna(dt):
                    return dt.strftime('%Y-%m-%d')
            except:
                pass
        # Fallback to smart parsing
        try:
            return pd.to_datetime(date_str).strftime('%Y-%m-%d')
        except:
            return None

    def validate_row(self, entity_type, row, source_info):
        # Get schema definition key
        def_key = entity_type.replace("Event", "") 
        validator = VALIDATORS.get(def_key)
        
        if not validator:
            logging.warning(f"No schema found for {entity_type}")
            return True

        try:
            # Basic type conversion before validation
            for col, val in row.items():
                if 'Count' in col or 'Days' in col:
                     try:
                         if pd.notna(val):
                             row[col] = int(val)
                     except:
                         pass
            
            validator.validate(row)
            return True
        except ValidationError as e:
            # Quarantine
            q_file = QUARANTINE_DIR / f"{source_info['study']}_{entity_type}_invalid.csv"
            row['error'] = e.message
            row_df = pd.DataFrame([row])
            header = not q_file.exists()
            row_df.to_csv(q_file, mode='a', header=header, index=False)
            return False

    def process_study(self, study_folder):
        study_id = study_folder.split('_')[1] # Study_1_Input_Files -> 1
        logging.info(f"Starting ingestion for Study {study_id}")
        
        files = list((SOURCE_DIR / study_folder).glob("*.xlsx"))
        
        # Register Study Entity
        self.store.add_entity("Study", {"StudyID": f"Study {study_id}"}, 
                              self.provenance.add_trace(study_id, "folder", 0, "Study", f"Study {study_id}"))

        for file_path in files:
            try:
                self.parse_file(study_id, file_path)
            except Exception as e:
                logging.error(f"Failed parsing file {file_path.name}: {e}")

    def parse_file(self, study_id, file_path):
        fname = file_path.name
        logging.info(f"  Parsing {fname}...")
        
        # Identify file type
        if "EDC_Metrics" in fname:
            self.parse_edc_metrics(study_id, file_path)
        elif "EDRR" in fname:
            self.parse_edrr(study_id, file_path)
        elif "MedDRA" in fname:
            self.parse_coding(study_id, file_path, "MedDRA")
        elif "WHODrug" in fname:
            self.parse_coding(study_id, file_path, "WHODrug")
        elif "Inactivated_Records" in fname:
            self.parse_inactivated(study_id, file_path)
        elif "Lab_Discrepancies" in fname:
            self.parse_lab(study_id, file_path)
        elif "Missing_Pages" in fname:
            self.parse_missing_pages(study_id, file_path)
        elif "Visit_Projection" in fname:
            self.parse_visit_projection(study_id, file_path)
        elif "SAE_Dashboard" in fname:
            self.parse_sae(study_id, file_path)
        else:
            logging.warning(f"Unknown file type: {fname}")

    def parse_edc_metrics(self, study_id, file_path):
        try:
            df = pd.read_excel(file_path, sheet_name="Query Report - Cumulative")
        except:
            logging.warning(f"Sheet 'Query Report - Cumulative' not found in {file_path}")
            return

        for idx, row in df.iterrows():
            if idx > 0 and idx % 2000 == 0: logging.info(f"    Processed {idx} queries...")
            source_info = {'study': study_id, 'file': file_path.name, 'row': idx}
            
            # 1. Site
            raw_site_id = str(row.get('Site Number', row.get('Site ID', '')))
            if pd.notna(raw_site_id) and raw_site_id != 'nan':
                 # Global Unique ID
                site_id = f"Study_{study_id}_{raw_site_id}"
                site_data = {
                    "SiteID": site_id,
                    "Country": row.get('Country'),
                    "Region": row.get('Region'),
                    "SiteName": f"Site {raw_site_id}" 
                }
                if self.validate_row("Site", site_data, source_info):
                    t_id = self.provenance.add_trace(study_id, file_path.name, idx, "Site", site_id)
                    self.store.add_entity("Site", site_data, t_id)

            # 2. Subject
            raw_subj_id = str(row.get('Subject Name', ''))
            if pd.notna(raw_subj_id) and raw_subj_id != 'nan':
                 # Global Unique ID
                subj_id = f"Study_{study_id}_{raw_subj_id}"
                subj_data = {
                    "SubjectID": subj_id,
                    "SubjectStatus": "Enrolled" 
                }
                if self.validate_row("Subject", subj_data, source_info):
                    t_id = self.provenance.add_trace(study_id, file_path.name, idx, "Subject", subj_id)
                    self.store.add_entity("Subject", subj_data, t_id)

            # 3. Query (Main Event)
            if pd.notna(row.get('Log #')):
                 q_id = f"Query_{study_id}_{row.get('Log #')}"
            else:
                 q_id = f"Query_{study_id}_{idx}"
            
            query_data = {
                "QueryID": q_id,
                "FieldOID": str(row.get('Field OID', '')),
                "QueryStatus": row.get('Query Status', 'Open'),
                "MarkingGroup": row.get('Marking Group Name'),
                "OpenDate": self.normalize_date(row.get('Query Open Date')),
                "ResponseDate": self.normalize_date(row.get('Query Response Date'))
            }
            status_map = {"Candidate": "Open", "Answered": "Answered", "Closed": "Closed", "Cancelled": "Cancelled", "Open": "Open"}
            query_data['QueryStatus'] = status_map.get(query_data['QueryStatus'], "Open")

            if self.validate_row("Query", query_data, source_info):
                t_id = self.provenance.add_trace(study_id, file_path.name, idx, "Query", q_id)
                self.store.add_entity("Query", query_data, t_id)

    def parse_missing_pages(self, study_id, file_path):
        try:
            df = pd.read_excel(file_path, sheet_name="All Pages Missing")
        except: return

        for idx, row in df.iterrows():
            source_info = {'study': study_id, 'file':file_path.name, 'row':idx}
            
            raw_subj = str(row.get('Subject Name', row.get('SubjectName', '')))
            if raw_subj and raw_subj != 'nan':
                subj_id = f"Study_{study_id}_{raw_subj}"
                self.store.add_entity("Subject", {"SubjectID": subj_id}, self.provenance.add_trace(study_id, file_path.name, idx, "Subject", subj_id))

            form_data = {
                "FormName": row.get('FormName', row.get('Page Name')),
                "IsMissing": True,
                "DaysMissing": row.get('No. #Days Page Missing', row.get('# of Days Missing'))
            }
            if self.validate_row("Form", form_data, source_info):
                 t_id = self.provenance.add_trace(study_id, file_path.name, idx, "Form", form_data['FormName'])
                 self.store.add_entity("Form", form_data, t_id)

    def parse_lab(self, study_id, file_path):
        try:
             df = pd.read_excel(file_path, sheet_name="Missing_Lab_Name_and_Missing")
        except: return

        for idx, row in df.iterrows():
            if row.get('Subject'):
                subj = str(row.get('Subject'))
                if subj != 'nan':
                    subj_id = f"Study_{study_id}_{subj}"
                    self.store.add_entity("Subject", {"SubjectID": subj_id}, 
                                        self.provenance.add_trace(study_id, file_path.name, idx, "Subject", subj_id))

            lab_data = {
                "TestName": row.get('Test Name'),
                "LabCategory": row.get('Lab category'),
                "LabDate": self.normalize_date(row.get('Lab Date')),
                "IssueType": row.get('Issue')
            }
            if self.validate_row("Lab", lab_data, {'study': study_id, 'file':file_path.name, 'row':idx}):
                 t_id = self.provenance.add_trace(study_id, file_path.name, idx, "Lab", str(idx))
                 self.store.add_entity("Lab", lab_data, t_id)

    def parse_sae(self, study_id, file_path):
        try:
            df = pd.read_excel(file_path, sheet_name="SAE Dashboard_Safety")
        except: return
        
        for idx, row in df.iterrows():
            pid = str(row.get('Patient ID'))
            sae_data = {
                "CaseID": f"{pid}-SAE", 
                "CaseStatus": row.get('Case Status'),
                "ReviewStatus": row.get('Review Status')
            }
            if self.validate_row("Safety", sae_data, {'study': study_id, 'file':file_path.name, 'row':idx}):
                 t_id = self.provenance.add_trace(study_id, file_path.name, idx, "Safety", sae_data['CaseID'])
                 self.store.add_entity("Safety", sae_data, t_id)

    def parse_coding(self, study_id, file_path, dict_type):
        sheet = "GlobalCodingReport_MedDRA" if dict_type == "MedDRA" else "GlobalCodingReport_WHODD"
        try:
            xl = pd.ExcelFile(file_path)
            sheet_name = sheet if sheet in xl.sheet_names else xl.sheet_names[0]
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except: return

        for idx, row in df.iterrows():
            coding_data = {
                "Dictionary": dict_type,
                "DictionaryVersion": row.get('Dictionary Version number'),
                "VerbatimTerm": row.get('Logline'),
                "CodingStatus": row.get('Coding Status')
            }
            if self.validate_row("Coding", coding_data, {'study': study_id, 'file':file_path.name, 'row':idx}):
                t_id = self.provenance.add_trace(study_id, file_path.name, idx, "Coding", str(idx))
                self.store.add_entity("Coding", coding_data, t_id)
    
    def parse_edrr(self, study_id, file_path):
        try:
            df = pd.read_excel(file_path, sheet_name="OpenIssuesSummary")
        except: return
        
        for idx, row in df.iterrows():
             raw_subj_id = str(row.get('Subject', ''))
             if raw_subj_id and raw_subj_id != 'nan':
                 subj_id = f"Study_{study_id}_{raw_subj_id}"
                 subj_data = {
                     "SubjectID": subj_id,
                     "OpenIssueCount": row.get('Total Open issue Count per subject')
                 }
                 if self.validate_row("Subject", subj_data, {'study': study_id, 'file': file_path.name, 'row': idx}):
                     t_id = self.provenance.add_trace(study_id, file_path.name, idx, "Subject", subj_id)
                     self.store.add_entity("Subject", subj_data, t_id)

    def parse_visit_projection(self, study_id, file_path):
        try:
            df = pd.read_excel(file_path, sheet_name="Missing Visits")
        except: return
        for idx, row in df.iterrows():
            if row.get('Subject'):
                subj = str(row.get('Subject'))
                if subj != 'nan':
                    subj_id = f"Study_{study_id}_{subj}"
                    self.store.add_entity("Subject", {"SubjectID": subj_id}, 
                                        self.provenance.add_trace(study_id, file_path.name, idx, "Subject", subj_id))

            visit_data = {
                "VisitName": row.get('Visit'),
                "ProjectedDate": self.normalize_date(row.get('Projected Date')),
                "DaysOutstanding": row.get('# Days Outstanding')
            }
            if self.validate_row("Visit", visit_data, {'study': study_id, 'file':file_path.name, 'row':idx}):
                t_id = self.provenance.add_trace(study_id, file_path.name, idx, "Visit", visit_data['VisitName'])
                self.store.add_entity("Visit", visit_data, t_id)

    def parse_inactivated(self, study_id, file_path):
        try:
             df = pd.read_excel(file_path, sheet_name=0) 
        except: return
        for idx, row in df.iterrows():
            inact_data = {
                "Folder": row.get('Folder'),
                "Form": row.get('Form'),
                "RecordPosition": str(row.get('RecordPosition')),
                "AuditAction": row.get('Audit Action')
            }
            if self.validate_row("Inactivation", inact_data, {'study': study_id, 'file':file_path.name, 'row':idx}):
                t_id = self.provenance.add_trace(study_id, file_path.name, idx, "Inactivation", str(idx))
                self.store.add_entity("Inactivation", inact_data, t_id)


def main():
    if not SOURCE_DIR.exists():
        logging.error(f"Source dir {SOURCE_DIR} not found.")
        return

    # Filter for processing specific studies if stuck
    # But for now, just process what is there.
    
    engine = IngestionEngine()
    
    study_folders = sorted([d.name for d in SOURCE_DIR.iterdir() if d.is_dir() and "Study_" in d.name])
    
    registry_rows = []
    
    for folder in study_folders:
        try:
            engine.process_study(folder)
            registry_rows.append({"study_folder": folder, "status": "ingested", "timestamp": datetime.datetime.now()})
        except Exception as e:
            logging.error(f"Failed study {folder}: {e}")
            registry_rows.append({"study_folder": folder, "status": "failed", "error": str(e)})

    # Save Registry
    pd.DataFrame(registry_rows).to_csv(CANONICAL_DIR / "study_registry.csv", index=False)

    # Save All Entities
    engine.store.save_all()
    
    # Save Provenance
    engine.provenance.save()

    print("Phase 2 Ingestion Complete.")

if __name__ == "__main__":
    main()
