import os
import pandas as pd
from typing import List, Dict, Union
import pprint

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

FIELD_ALIASES = {
    "resume": ["cv", "resume_str"],
    "summary": ["profile", "about"],
    "skills": ["skillset", "technical_skills","related_skills","related_skills_in_job","related_skills_in_previous_jobs","responsibilities"],
    "position": ["category","experience","positions","work_history", "employment","previous_jobs","job_history","work_experience","previous_positions","job_position_name"],
    "education": ["academic", "schooling", "degree_names", "degrees"],
    "major": ["degree_major", "major_subject", "major_field_of_study", "major_field","field_of_study","field_of_studies"],
    "educational_records": ["academic_records", "degree_records","educational_results"],
    "result_type": ["result_types"],
    "graduation_year": ["passing_years", "graduation"],
    "certifications": ["licenses", "certs","certification_providers","certification_skills", ],
    "projects": ["portfolio", "work_samples"],
    "languages": ["language_skills"],
}


BAD_VALUES = {"n/a", "na", "none", "null", "", "['n/a']", "[none]", "[nan]"}

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
    
def normalize_column(col: str) -> str:
    col = col.strip().lower().replace(" ", "_")
    for std_field, aliases in FIELD_ALIASES.items():
        if col == std_field or col in aliases:
            return std_field
    return col  # fallback

def clean_value(val):
    if isinstance(val, list):
        val = [str(v).strip() for v in val if str(v).strip().lower() not in BAD_VALUES]
        return val if val else []
    elif isinstance(val, str):
        val_clean = val.strip()
        return "Not Provided" if val_clean.lower() in BAD_VALUES else val_clean
    elif pd.isna(val):
        return "Not Provided"
    return val

def is_resume_valid(resume_dict: Dict) -> bool:
    # Require at least 3 non-empty fields (excluding 'resume' and metadata)
    core_fields = [k for k in resume_dict if k != "resume" and resume_dict[k]]
    return len(core_fields) >= 3

def map_to_schema(row: pd.Series) -> Dict:
    structured = BASE_SCHEMA.copy()
    for col, value in row.items():
        key = normalize_column(col)
        if key in structured:
            cleaned = clean_value(value)
            if isinstance(structured[key], list):
                structured[key] = cleaned if isinstance(cleaned, list) else [cleaned]
            else:
                structured[key] = cleaned
    return structured

def process_datasets(file_paths: List[str]) -> List[Dict]:
    all_resumes = []
    for path in file_paths:
        df = load_dataset(path)
        df = df.fillna("")  # avoid NaNs
        for _, row in df.iterrows():
            structured_resume = map_to_schema(row)
            all_resumes.append(structured_resume)
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
    input("Press Enter to continue...")
    
    n=2484+962
    pprint.pprint(resumes[n])
    print(data2.iloc[0])