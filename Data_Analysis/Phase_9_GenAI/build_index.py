import pandas as pd
import json
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_PATH = os.path.join(BASE_DIR, "../Phase_3_Risk_Signals/Signal_Data/signals.parquet")
PROVENANCE_PATH = os.path.join(BASE_DIR, "../Phase_2_Ingestion/Canonical_Data/provenance.parquet")
OUTPUT_PATH = os.path.join(BASE_DIR, "../../web-app/src/data/provenance_index.json")

def build_index():
    print("Loading datasets...")
    try:
        if not os.path.exists(SIGNALS_PATH):
            print(f"Error: {SIGNALS_PATH} not found.")
            return
        if not os.path.exists(PROVENANCE_PATH):
             # Try fallback location or skip if strictly required
             print(f"Warning: {PROVENANCE_PATH} not found. Proceeding with signals only.")
             prov_df = pd.DataFrame() 
        else:
             prov_df = pd.read_parquet(PROVENANCE_PATH)

        signals_df = pd.read_parquet(SIGNALS_PATH)
    except Exception as e:
        print(f"Error reading parquet files: {e}")
        return

    print(f"Loaded {len(signals_df)} signals.")
    
    # We want a map: signal_id -> { signal_details, provenance_rows: [] }
    # Assuming 'trace_id' or 'row_id' links them. 
    # If explicit link missing in current data, we will mock the linkage for the demo.
    
    index = {}
    
    # Iterate over signals and build the index
    # Limit to top 1000 for performance if needed, or full if small.
    # signals.parquet likely has: signal_id, subject_id, study_id, message, etc.
    
    # Limit to top 2000 for performance
    signals_df = signals_df.head(2000)
    
    records = signals_df.to_dict(orient='records')
    
    # Helper to clean data for JSON
    def clean_for_json(obj):
        if hasattr(obj, 'tolist'): # Check for numpy array
            return obj.tolist()
        if pd.isna(obj): # Check for NaN
            return None
        return obj

    for row in records:
        sig_id = row.get('signal_id') or row.get('id') # Fallback
        if not sig_id: continue
        
        # Clean the row data
        cleaned_row = {k: clean_for_json(v) for k, v in row.items()}
        
        index[sig_id] = {
            "signal": cleaned_row,
            "provenance": [] 
        }

    print(f"Built index with {len(index)} keys. Saving to {OUTPUT_PATH}...")
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(index, f, indent=2)
        
    print("Done.")

if __name__ == "__main__":
    build_index()
