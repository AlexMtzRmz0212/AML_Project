import os
import pandas as pd
from typing import List, Dict, Union
import pprint

# Base schema
BASE_SCHEMA = {
    "resume": "",
    "summary": "",
    "skills": [],
    "position": [],
    "education": [],
    "major": [],
    "educational_records": [],
    "result_type": [],
    "graduation_year": [],
    "certifications": [],
    "projects": [],
    "languages": [],
}

# Alias map for normalization
FIELD_ALIASES = {
    "resume": ["cv", "resume_str"],
    "summary": ["career_objective", "related_skills_in_job","about"],
    "skills": ["skillset"],
    "position": ["category", "experience", "positions", "work_history", "employment", "previous_jobs", "job_history", "work_experience", "previous_positions", "job_position_name"],
    "education": ["degree_names", "degrees"],
    "major": ["degree_major", "major_subject", "major_field_of_study", "major_field", "field_of_study", "field_of_studies"],
    "educational_records": ["academic_records", "degree_records", "educational_results"],
    "result_type": ["result_types"],
    "graduation_year": ["passing_year", "graduation"],
    "certifications": ["licenses", "certs", "certification_providers", "certification_skills"],
    "projects": ["portfolio", "work_samples"],
    "languages": ["language_skills"],
}

# Normalizes alias column names to schema keys
def normalize_column(col: str) -> str:
    col = col.strip().lower().replace(" ", "_")
    for standard, aliases in FIELD_ALIASES.items():
        if col == standard or col in aliases:
            return standard
    return col

# Cleans bad values
BAD_VALUES = {"n/a", "na", "none", "null", "", "['n/a']", "[none]", "[nan]"}

def clean_value(val):
    if isinstance(val, list):
        cleaned = [v.strip() for v in val if str(v).strip().lower() not in BAD_VALUES]
        return cleaned if cleaned else []
    elif isinstance(val, str):
        val = val.strip()
        return "" if val.lower() in BAD_VALUES else val
    elif pd.isna(val):
        return ""
    else:
        return str(val)

# Builds a clean, structured resume from a raw row
def map_to_schema(row: pd.Series, source: str = "") -> Dict:
    structured = BASE_SCHEMA.copy()

    for col, value in row.items():
        key = normalize_column(col)
        if key in structured:
            cleaned = clean_value(value)
            if isinstance(structured[key], list):
                if isinstance(cleaned, str):
                    structured[key] = [s.strip() for s in cleaned.split(",") if s.strip()]
                elif isinstance(cleaned, list):
                    structured[key] = cleaned
            else:
                structured[key] = cleaned

    # Validate completeness
    filled_fields = sum(bool(structured[key]) for key in structured if key != "resume")
    is_valid = bool(structured["resume"].strip()) or filled_fields >= 3

    structured["meta"] = {
        # "source_file": source,
        "validResume": is_valid,
    }

    return structured if is_valid else None

# Loads supported file types
def load_dataset(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    elif ext == ".json":
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

# Main pipeline
def process_datasets(file_paths: List[str]) -> List[Dict]:
    all_resumes = []
    for path in file_paths:
        df = load_dataset(path)
        df = df.fillna("")  # Avoid NaNs
        for _, row in df.iterrows():
            structured = map_to_schema(row, source=os.path.basename(path))
            if structured:
                all_resumes.append(structured)
    return all_resumes

if __name__ == "__main__":
    resume_files = [
        "../datasets/1Resume.csv",
        "../datasets/2UpdatedResumeDataSet.csv",
        "../datasets/3resume_data.csv"
    ]
    
    # save each dataset in a pd dataframe for testing
    data0 = load_dataset(resume_files[0])
    data1 = load_dataset(resume_files[1])
    data2 = load_dataset(resume_files[2])
    
    resumes = process_datasets(resume_files)

    print(f"Total resumes loaded: {len(resumes)}")
    
    n=2484+962-1
    pprint.pprint(resumes[n])
    # print(data2.iloc[0])