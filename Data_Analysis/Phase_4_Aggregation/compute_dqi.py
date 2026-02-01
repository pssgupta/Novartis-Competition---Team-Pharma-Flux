import os
import pandas as pd
import json
import numpy as np
import datetime
from pathlib import Path

# Configuration
BASE_DIR = Path("/Users/mypro16/Desktop/Novaratis/Data for problem Statement 1")
SIGNAL_FILE = BASE_DIR / "Phase_3_Risk_Signals/Signal_Data/signals.parquet"
OUTPUT_DIR = BASE_DIR / "Phase_4_Aggregation/DQI_Data"
CONFIG_FILE = BASE_DIR / "Phase_4_Aggregation/Config/weights.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

class DQIEngine:
    def __init__(self):
        self.load_config()
        self.load_signals()

    def load_config(self):
        with open(CONFIG_FILE, 'r') as f:
            self.config = json.load(f)
        self.weights = self.config['weights']
        # Normalize weights just in case
        total_w = sum(self.weights.values())
        if total_w > 0:
            self.weights = {k: v/total_w for k, v in self.weights.items()}

    def load_signals(self):
        if not SIGNAL_FILE.exists():
            print("CRITICAL: No signals.parquet found.")
            return
        self.signals = pd.read_parquet(SIGNAL_FILE)
        print(f"Loaded {len(self.signals)} signals.")

    def get_risk_level(self, score):
        thresh = self.config['severity_thresholds']
        if score > thresh['High']: return "Critical"
        if score > thresh['Medium']: return "High"
        if score > thresh['Low']: return "Medium"
        return "Low"

    def compute_dqi(self):
        if self.signals.empty: return

        # Enforce numeric score
        self.signals['normalized_score'] = pd.to_numeric(self.signals['normalized_score'], errors='coerce').fillna(0)
        
        # Apply Weights
        # Map domain to weight
        # If domain not in config, use default small weight
        self.signals['weight'] = self.signals['domain'].map(lambda d: self.weights.get(d, 0.05))
        
        # Compute Weighted Score per Signal
        self.signals['weighted_score'] = self.signals['normalized_score'] * self.signals['weight']
        
        # Aggregation Logic
        # We want to aggregate by (Study, Entity Type, Entity ID)
        
        self.aggregate_entity("Site")
        self.aggregate_entity("Subject")
        # Can also do Visit if needed, but Site/Subject are main DQI drivers
        
    def aggregate_entity(self, entity_type):
        print(f"Aggregating DQI for {entity_type}...")
        
        # Filter signals relevant to this entity type
        # Note: Subject signals roll up to Site? 
        # For now, let's keep them distinct as per 'Ranked Priority Views' requirement
        
        if entity_type == "Site":
            # Site DQI should Ideally include Subject signals belonging to that site.
            # But the 'entity_type' in signals row corresponds to the granular entity.
            # 'Subject' entity rows have study_id, and entity_id (Study_X_Subject_Y).
            # To roll up Subject -> Site, we need to parse SiteID from SubjectID or have it in data.
            # In Phase 2, SubjectID is "Study_10_Subject 3507". It doesn't strictly contain Site info in ID string.
            # However,  and  exist. 
            # Phase 4 "No provenance joins" rule suggests we use what we have in signals.
            # If signals.parquet doesn't have SiteID for a subject signal, we can't roll up easily WITHOUT looking up.
            # BUT, the prompt says "Phase 4 takes signals.parquet".
            # If we want Site DQI to reflect Subject risk, we need that link.
            # Let's stick to strict Entity Aggregation first (Subject gets Subject Score).
            # Site signals (like "Coding Backlog") get Site Score.
            pass

        df_subset = self.signals[self.signals['entity_type'] == entity_type].copy()
        
        if df_subset.empty:
            print(f"No signals found for {entity_type}")
            return

        # Group by Entity
        # Sum of weighted scores? Average? 
        # A simple Sum can grow unbounded with volume, which is good for "Workload", 
        # but DQI usually implies 0-1 or 0-100 quality score.
        # Let's use: Sum(Weighted Scores) capped or normalized?
        # The prompt says: "sum ( signal.normalized_score * domain_weight )"
        # This implies it's cumulative risk. A site with 10 problems is worse than 1.
        # So we won't average. We will Sum.
        # But we might clamp it for the visual "DQI Score" 0-1 if desired, or keep it open.
        # "DQI Score ... 0 - 1" -> This suggests normalization.
        # How to normalize a Sum? 
        # Option: 1 - (1 / (1 + Sum)). Sigmoid? 
        # Or just Sum and then define Thresholds for categorization.
        # Let's use Sum for "Risk Score" and then a Sigmoid function for "Index (0-1)".
        
        grouped = df_subset.groupby(['study_id', 'entity_id']).agg(
            total_weighted_risk=('weighted_score', 'sum'),
            signal_count=('signal_id', 'count'),
            top_domains=('domain', lambda x: list(x.value_counts().index[:3]))
        ).reset_index()
        
        # Compute Index (0-1)
        # Using a simple tanh or sigmoid to squash 0-inf to 0-1
        # Risk 5.0 is incredibly high. Risk 0.1 is low.
        # dqi = tanh(risk) covers 0 to 1 well.
        grouped['dqi_score'] = np.tanh(grouped['total_weighted_risk'])
        
        grouped['risk_level'] = grouped['dqi_score'].apply(self.get_risk_level)
        grouped['generated_at'] = datetime.datetime.now().isoformat()
        
        # Save
        outfile = OUTPUT_DIR / f"ranked_{entity_type.lower()}s.csv"
        # Join top domain nicely
        grouped['top_domains'] = grouped['top_domains'].apply(lambda x: "|".join(x))
        
        grouped.sort_values('dqi_score', ascending=False).to_csv(outfile, index=False)
        print(f"Saved {len(grouped)} rows to {outfile}")

    def run(self):
        self.compute_dqi()
        print("Phase 4 DQI Complete.")

if __name__ == "__main__":
    engine = DQIEngine()
    engine.run()
