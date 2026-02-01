import os
import pandas as pd
import numpy as np
import uuid
import datetime
from pathlib import Path

# Configuration
BASE_DIR = Path("/Users/mypro16/Desktop/Novaratis/Data for problem Statement 1")
CANONICAL_DIR = BASE_DIR / "Phase_2_Ingestion/Canonical_Data"
OUTPUT_DIR = BASE_DIR / "Phase_3_Risk_Signals/Signal_Data"

# Ensure output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

class SignalEngine:
    def __init__(self):
        self.signals = []
        self.load_data()

    def load_data(self):
        print("Loading canonical data...")
        self.dfs = {}
        for entity in ['study', 'site', 'subject', 'visit', 'form', 'query', 'lab', 'safety', 'coding', 'inactivation', 'provenance']:
            p_path = CANONICAL_DIR / f"{entity}.parquet"
            if p_path.exists():
                self.dfs[entity] = pd.read_parquet(p_path)
            else:
                print(f"Warning: {entity} data not found.")
                self.dfs[entity] = pd.DataFrame()

    def normalize_score(self, raw_val, max_val):
        return min(max(raw_val / max_val, 0.0), 1.0)
    
    def get_severity(self, score):
        if score > 0.8: return "Critical"
        if score > 0.5: return "High"
        if score >= 0.2: return "Medium"
        return "Low"

    def add_signal(self, name, domain, entity_type, entity_id, study_id, raw_val, norm_score, explanation, trace_ids):
        self.signals.append({
            "signal_id": str(uuid.uuid4())[:8],
            "signal_name": name,
            "domain": domain,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "study_id": study_id,
            "raw_metric_value": raw_val,
            "normalized_score": round(norm_score, 4),
            "severity_level": self.get_severity(norm_score),
            "explanation": explanation,
            "trace_ids": trace_ids, # Keep as list
            "signal_timestamp": datetime.datetime.now().isoformat()
        })

    def run_all(self):
        self.domain_1_edc()
        self.domain_2_visits()
        self.domain_3_queries()
        self.domain_4_labs()
        self.domain_5_safety_coding()
        self.save()

    # --- DOMAIN 1: EDC DATA COMPLETENESS ---
    def domain_1_edc(self):
        print("Running Domain 1: EDC Completeness...")
        
        # 1. Missing Pages / overdue CRFs (Form entity)
        df_form = self.dfs.get('form')
        if not df_form.empty:
            # Join with provenance to get StudyID if needed, or parse from trace_id/entity_id? 
            # Actually most entities have study context in their ID or we can infer it.
            # Entity IDs are like "Study_10_Subject_X".
            
            # Group by Subject to count missing pages
            # We assume df_form contains 'IsMissing'=True rows based on Phase 2 logic
            
            for index, row in df_form.iterrows():
                if row.get('IsMissing'):
                    # Signal: Single Missing Form (High Granularity)
                    raw_days = row.get('DaysMissing', 0)
                    try: 
                        raw_days = int(raw_days)
                    except: 
                        raw_days = 0
                    
                    # Normalize: >90 days is 1.0
                    score = self.normalize_score(raw_days, 90)
                    
                    # Extract Study ID from Subject ID logic or trace?
                    # Using the first part of trace_id lookup is expensive. 
                    # Let's verify if we have StudyID in the entity tables.
                    # Phase 2 tables:  has [FormName, IsMissing, DaysMissing, trace_id]
                    # We might need to join with provenance to get Study ID easily.
                    
                    # Optimization: extract from FormName or assume lineage is needed.
                    # For now, let's look at the trace_id in provenance.
                    pass 

        # Optimization: Create a Trace->Study map
        print("  Mapping Trace IDs...")
        # We need source info for linking
        prov = self.dfs['provenance']
        
        # --- Signal 1: Missing Pages (Aggregated by Subject) ---
        # Get missing forms
        forms = self.dfs['form']
        if not forms.empty:
            # Merge with provenance to get Subject and Study context
            # Form entity in Phase 2 didn't store SubjectID explicitly? 
            # In parse_missing_pages: 
            # The Form entity itself in Phase 2 schema is: Name, IsMissing, DaysMissing.
            # It DOES NOT have SubjectID. This is a GAP in Phase 2 Schema?
            # Wait,  has  which for Form is . 
            # Usually FormName isn't unique across subjects. 
            # Let's hope Phase 2 Logic linked it correctly.
            # In Phase 2 :
            #   
            #   
            # The provenance has . If  is just "FormName", we can't accept it.
            # Let's check  content.
            # If provenance  is generic "Visit 1", we lost the subject link!
            # BUT, the  row also has  and .
            # All entities from the same row belong to the same Subject context.
            
            # RECOVERY STRATEGY:
            # We need to link Form -> Provenance -> Row -> Subject (defined in same row).
            # This is "Explainability" in action.
            
            # 1. Get all Form traces
            form_traces = prov[prov['canonical_entity'] == 'Form']
            # 2. Get all Subject traces
            subj_traces = prov[prov['canonical_entity'] == 'Subject']
            
            # 3. Join on (study_id, source_file, source_row_number)
            # This links the Form on Row X to the Subject on Row X.
            merged = pd.merge(
                form_traces, 
                subj_traces[['study_id', 'source_file', 'source_row_number', 'entity_id']], 
                on=['study_id', 'source_file', 'source_row_number'],
                suffixes=('_form', '_subj')
            )
            # Now we have form_trace_id -> SubjectID
            
            # Add Missing Page Signals
            # Get DaysMissing from valid forms
            missing_forms = forms[forms['IsMissing'] == True]
            # Join with the context
            # Note: since subj_traces didn't have trace_id in projection, 'trace_id' from form_traces is kept as 'trace_id'
            work_df = pd.merge(missing_forms, merged, on='trace_id')
            
            for idx, row in work_df.iterrows():
                days = row.get('DaysMissing', 0)
                try: days = int(days)
                except: days = 0
                
                score = self.normalize_score(days, 60) # 60 days late = critical
                
                self.add_signal(
                    name="Overdue CRF / Missing Page",
                    domain="EDC Completeness",
                    entity_type="Subject",
                    entity_id=row['entity_id_subj'], # The SubjectID
                    study_id=row['study_id'],
                    raw_val=days,
                    norm_score=score,
                    explanation=f"Form '{row['FormName']}' is missing for {days} days.",
                    trace_ids=[row['trace_id']]
                )

    # --- DOMAIN 2: VISIT COMPLIANCE ---
    def domain_2_visits(self):
        print("Running Domain 2: Visits...")
        visits = self.dfs.get('visit')
        if visits.empty: return
        
        prov = self.dfs['provenance']
        visit_traces = prov[prov['canonical_entity'] == 'Visit']
        subj_traces = prov[prov['canonical_entity'] == 'Subject']
        
        # Link Visit -> Subject via Source Row
        merged = pd.merge(
            visit_traces,
            subj_traces[['study_id', 'source_file', 'source_row_number', 'entity_id']],
            on=['study_id', 'source_file', 'source_row_number'],
            suffixes=('_visit', '_subj')
        )
        
        work_df = pd.merge(visits, merged, on='trace_id')
        
        for idx, row in work_df.iterrows():
            days = row.get('DaysOutstanding', 0)
            try: days = int(days)
            except: days = 0
            
            if days > 0:
                score = self.normalize_score(days, 30) # 30 days late = critical
                self.add_signal(
                    name="Visit Delay",
                    domain="Visit Compliance",
                    entity_type="Subject",
                    entity_id=row['entity_id_subj'],
                    study_id=row['study_id'],
                    raw_val=days,
                    norm_score=score,
                    explanation=f"Visit '{row['VisitName']}' is outstanding for {days} days.",
                    trace_ids=[row['trace_id']]
                )

    # --- DOMAIN 3: QUERIES ---
    def domain_3_queries(self):
        print("Running Domain 3: Queries...")
        queries = self.dfs.get('query')
        if queries.empty: return

        prov = self.dfs['provenance']
        q_traces = prov[prov['canonical_entity'] == 'Query']
        
        # Query ID usually contains Study ID, but let's use provenance for StudyID
        work_df = pd.merge(queries, q_traces[['trace_id', 'study_id']], on='trace_id')
        
        # Calculate Query Age (assuming today is fixed reference or using meta)
        # Using a fixed reference date for demo purposes or 'Ingestion Date'
        # Actually OpenDate is in the PARQUET.
        
        today = pd.to_datetime('today')
        
        for idx, row in work_df.iterrows():
            status = row.get('QueryStatus')
            if status == 'Open':
                open_date = pd.to_datetime(row.get('OpenDate'), errors='coerce')
                age = 0
                if pd.notna(open_date):
                    age = (today - open_date).days
                
                score = self.normalize_score(age, 45) # 45 days open = critical
                
                self.add_signal(
                    name="Open Query Risk",
                    domain="Query Health",
                    entity_type="Query", # Identifying the specific query
                    entity_id=row['QueryID'],
                    study_id=row['study_id'],
                    raw_val=age,
                    norm_score=score,
                    explanation=f"Query {row['QueryID']} has been open for {age} days.",
                    trace_ids=[row['trace_id']]
                )

    # --- DOMAIN 4: LABS ---
    def domain_4_labs(self):
        print("Running Domain 4: Labs...")
        labs = self.dfs.get('lab')
        if labs.empty: return
        
        # Lab issues are rows in the lab table (based on Phase 2 logic)
        # Join prov for StudyID
        prov = self.dfs['provenance']
        l_traces = prov[prov['canonical_entity'] == 'Lab']
        work_df = pd.merge(labs, l_traces[['trace_id', 'study_id']], on='trace_id')
        
        for idx, row in work_df.iterrows():
            issue = row.get('IssueType', 'Unknown')
            # Any row here is an issue
            self.add_signal(
                name="Lab Data Issue",
                domain="Lab Integrity",
                entity_type="Lab",
                entity_id=f"Lab_{idx}",
                study_id=row['study_id'],
                raw_val=1,
                norm_score=0.8, # Default high for data integrity
                explanation=f"Lab discrepancy found: {issue}",
                trace_ids=[row['trace_id']]
            )

    # --- DOMAIN 5: SAFETY ---
    def domain_5_safety_coding(self):
        print("Running Domain 5: Safety/Coding...")
        
        # Coding
        coding = self.dfs.get('coding')
        if not coding.empty:
            prov = self.dfs['provenance']
            c_traces = prov[prov['canonical_entity'] == 'Coding']
            work_df = pd.merge(coding, c_traces[['trace_id', 'study_id']], on='trace_id')
            
            for idx, row in work_df.iterrows():
                status = row.get('CodingStatus')
                if status != 'Coded': # Assuming 'Coded' is the good state
                    self.add_signal(
                         name="Uncoded Term",
                         domain="Coding Readiness",
                         entity_type="Coding",
                         entity_id=f"Code_{idx}",
                         study_id=row['study_id'],
                         raw_val=1,
                         norm_score=0.6,
                         explanation=f"Term '{row.get('VerbatimTerm')}' is not coded.",
                         trace_ids=[row['trace_id']]
                    )
                    
        # Safety
        safety = self.dfs.get('safety')
        if not safety.empty:
            # Check for non-closed cases?
            prov = self.dfs['provenance']
            s_traces = prov[prov['canonical_entity'] == 'Safety']
            work_df = pd.merge(safety, s_traces[['trace_id', 'study_id']], on='trace_id')
            
            for idx, row in work_df.iterrows():
                status = row.get('ReviewStatus')
                if isinstance(status, str) and 'Review' not in status: # Heuristic
                     pass
                # Just flagging all open SAEs for now as Medium risk
                self.add_signal(
                    name="SAE Attention Required",
                    domain="Safety",
                    entity_type="SafetyCase",
                    entity_id=row.get('CaseID'),
                    study_id=row['study_id'],
                    raw_val=1,
                    norm_score=0.5,
                    explanation=f"SAE Case {row.get('CaseID')} status: {row.get('CaseStatus')}",
                    trace_ids=[row['trace_id']]
                )

    def save(self):
        print(f"Saving {len(self.signals)} signals...")
        if not self.signals:
            print("No signals generated.")
            return

        df = pd.DataFrame(self.signals)
        
        # Convert trace_ids list to string for CSV compatibility (Parquet can handle lists)
        # We will save parquet as primary
        
        out_parquet = OUTPUT_DIR / "signals.parquet"
        out_csv = OUTPUT_DIR / "signals.csv"
        
        df.to_parquet(out_parquet, index=False)
        
        # For CSV, join explainability
        df_csv = df.copy()
        df_csv['trace_ids'] = df_csv['trace_ids'].apply(lambda x: '|'.join(x))
        df_csv.to_csv(out_csv, index=False)
        print("Done.")

if __name__ == "__main__":
    engine = SignalEngine()
    engine.run_all()
