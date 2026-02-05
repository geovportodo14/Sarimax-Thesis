import os
import sys

# Add current directory to path so we can import the stages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from TH2_Mongo_Extractor import extract_mongo_data
import importlib

# Stage A
stage_a = importlib.import_module("stage_a_standardization")
# Stage B
stage_b = importlib.import_module("stage_b_cleaning")
# Stage C
stage_c = importlib.import_module("stage_c_features")
# Stage D
stage_d = importlib.import_module("stage_d_export")

def run_full_pipeline():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    
    raw_dir = os.path.join(project_root, "data/raw")
    inter_dir = os.path.join(project_root, "data/intermediate")
    final_dir = os.path.join(project_root, "data/final")
    
    os.makedirs(inter_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

    print("=== Phase 0: Extraction from MongoDB Atlas ===")
    extract_mongo_data()
    
    print("\n=== Phase 1: Stage A - Integrity and Standardization ===")
    result_a = stage_a.stage_331_integrity_verification(
        smartplug_csv_path=os.path.join(raw_dir, "smartplug_raw.csv"),
        weather_csv_path=os.path.join(raw_dir, "weather_raw.csv")
    )
    # Save intermediate
    sp_stage_a = os.path.join(inter_dir, "smartplug_stageA.csv")
    wx_stage_a = os.path.join(inter_dir, "weather_stageA.csv")
    result_a["smartplug_std"].to_csv(sp_stage_a, index=False)
    result_a["weather_std"].to_csv(wx_stage_a, index=False)
    print("Stage A Complete.")

    print("\n=== Phase 2: Stage B - Cleaning and Energy Derivation ===")
    result_b = stage_b.stage_332_cleaning_and_energy_derivation(
        smartplug_stage331_path=sp_stage_a
    )
    sp_stage_b = os.path.join(inter_dir, "smartplug_stageB.csv")
    result_b["df_stage332"].to_csv(sp_stage_b, index=False)
    print("Stage B Complete.")

    print("\n=== Phase 3: Stage C - Aggregation and Feature Construction ===")
    result_c = stage_c.stage_333_aggregation_and_features(
        smartplug_stage332_path=sp_stage_b,
        weather_path=wx_stage_a
    )
    sp_stage_c = os.path.join(inter_dir, "smartplug_stageC.csv")
    result_c["hourly_features_df"].to_csv(sp_stage_c, index=False)
    print("Stage C Complete.")

    print("\n=== Phase 4: Stage D - Final Modeling Dataset ===")
    result_d = stage_d.stage_334_final_transformation(
        hourly_features_stage333_path=sp_stage_c,
        output_dir=final_dir
    )
    print(f"Stage D Complete. Final files saved in {final_dir}")

if __name__ == "__main__":
    run_full_pipeline()
