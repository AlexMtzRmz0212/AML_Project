import os
import pandas as pd
from typing import List, Dict, Union
import pprint
import ast
import json

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

# (col: str) -> str means the function takes a string as input and returns a string
def normalize_column(col: str) -> str: 
    """Normalizes column names to match the schema keys."""
    # .strip() removes leading and trailing whitespace
    # .lower() converts to lowercase
    # .replace(" ", "_") replaces spaces with underscores
    col = col.strip().lower().replace(" ", "_")
    # for each standard field name
    for standard, aliases in FIELD_ALIASES.items():
        # check if the column name matches or is an alias
        if col == standard or col in aliases:
            # if so, return the standard field name
            return standard
    # if not, return the original column name
    return col

# Cleans bad values
BAD_VALUES = {"n/a", "na", "none", "null", "", "['n/a']", "[none]", "[nan]"}

def clean_value(val):
    """Cleans and normalizes values."""
    # isinstance checks the type of val
    # if val is a list
    if isinstance(val, list):
        # it will iterate through the list and check if each value is in BAD_VALUES
        cleaned = [v.strip() for v in val if str(v).strip().lower() not in BAD_VALUES]
        # if the cleaned list is not empty, return it
        # else, return an empty list
        return cleaned if cleaned else []
    
    # if val is a string
    elif isinstance(val, str):
        # it will strip leading and trailing whitespace
        val = val.strip()
        # it will check if the value is in BAD_VALUES
        # if so, return an empty string
        if val.lower() in BAD_VALUES:
            return ""
        
        # if the value is a string representation of a list
        if val.startswith("[") and val.endswith("]"):
            # it will try to parse it using ast.literal_eval
            try:
                # ast.literal_eval safely evaluates the string
                # and converts it to a Python object
                parsed = ast.literal_eval(val) 
                # if the parsed value is a list
                if isinstance(parsed, list):
                    # it will iterate through the list and check if each value is in BAD_VALUES
                    # and return a cleaned list
                    return [str(v).strip() for v in parsed if str(v).strip().lower() not in BAD_VALUES]
            # if it fails to parse, it will fall back to treating it as a string
            except (SyntaxError, ValueError):
                # pass means do nothing on the exception
                pass  # fallback to string
        # return the cleaned value
        return val
    # if val is na or None
    # it will return an empty string
    elif pd.isna(val):
        return ""
    
    # else, it returns the value as a string
    else:
        return str(val)


def map_to_schema(row: pd.Series, source: str = "") -> Dict:
    """Builds a clean, structured resume from a raw row
 (row: pd.Series, source: str = "") -> Dict 
 means the function takes a pandas Series and an optional string as input
 and returns a dictionary
 row: pd.Series is a single row of a pandas DataFrame
 source: str = "" is an optional string that represents the source of the data"""
    
    # Initialize the structured dictionary with the base schema
    # to be used as a template for the structured resume
    structured = BASE_SCHEMA.copy()

    # it will iterate through each column and value in the row
    # row.items() returns a list of tuples (column name, value)
    # col is the column name and value is the value in that column
    for col, value in row.items():
        # normalize the column name
        key = normalize_column(col)
        # if the column name is not in the schema, skip it
        cleaned = clean_value(value)

        # if the normalized column name is in the schema
        if key in structured:
            # if the the column name compared with the schema is a list
            if isinstance(structured[key], list):
                # Combine values if already exists
                existing = structured[key]
                new_items = []
                # if the cleaned value is a string
                if isinstance(cleaned, str):
                    # it will split the string by commas
                    # and strip leading and trailing whitespace
                    new_items = [s.strip() for s in cleaned.split(",") if s.strip()]
                # if the cleaned value is a list
                elif isinstance(cleaned, list):
                    # means that it is a new item
                    new_items = cleaned
                # Combine existing and new items
                combined = existing + new_items
                # Remove duplicates and empty strings
                combined = [item.lower() for item in combined]
                # the schema key will be updated with the combined list
                # list(dict.fromkeys()) removes duplicates while preserving order
                # and the list comprehension filters out empty strings
                structured[key] = list(dict.fromkeys([item for item in combined if item]))
            else:
                if not structured[key] and cleaned:  # Only assign if not already set
                    structured[key] = cleaned

    # Check for validity
    # filled_fields counts the number of non-empty fields
    # it will iterate through the structured dictionary
    # and check if the value is not empty
    # and the key is not "resume"
    # it will sum the number of non-empty fields
    filled_fields = sum(bool(structured[key]) for key in structured if key != "resume")
    # is_valid checks if the resume field is not empty
    # or if the number of filled fields is greater than or equal to 3
    is_valid = bool(structured["resume"].strip()) or filled_fields >= 3

    # the dictionary in the meta key will be updated with the validity of the resume
    structured["meta"] = {
        "validResume": is_valid,
    }

    # if the resume is valid, it will return the structured dictionary
    # else, it will return None
    return structured if is_valid else None

# Loads supported file types
# this is for scalability to support more file types in the future
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
# (file_paths: List[str]) -> List[Dict] means the function takes a list of strings as input
# and returns a list of dictionaries
def process_datasets(file_paths: List[str]) -> List[Dict]:
    all_resumes = []
    # it will iterate through each file path in the list
    for path in file_paths:
        # it will load the dataset as a pandas DataFrame
        df = load_dataset(path)
        df = df.fillna("")  # Avoid NaNs
        # it will iterate through each row in the DataFrame
        # df.iterrows() returns an iterator that yields index and row data
        for _, row in df.iterrows():
            # it will map the row to the schema
            structured = map_to_schema(row, source=os.path.basename(path))
            # if the structured dictionary is not None
            # it will append it to the all_resumes list
            if structured:
                all_resumes.append(structured)
    return all_resumes

# function inside a function
def fill_empty_fields(data_list):
    """Replaces empty fields with a default value."""
    def replace_empty(value):
        """Recursively replaces empty fields with 'not provided'."""
        # if the value is a list and empty, return ["not provided"]
        if isinstance(value, list) and not value:
            return ["not provided"]
        # if the value is a string and empty, return "not provided"
        elif isinstance(value, str) and not value.strip():
            return "not provided"
        # if the value is a dictionary
        elif isinstance(value, dict):
            # it will iterate through the dictionary
            # and replace empty fields with "not provided"
            # it will return a new dictionary with the same keys and values
            # but with empty fields replaced
            return {k: replace_empty(v) for k, v in value.items()}
        return value
    # return a new list of dictionaries
    return [{k: replace_empty(v) for k, v in instance.items()} for instance in data_list]



if __name__ == "__main__":
    # List of resume files PATHS to process
    resume_files = [
        "../datasets/1Resume.csv",
        "../datasets/2UpdatedResumeDataSet.csv",
        "../datasets/3resume_data.csv"
    ]
    
    # save each dataset in a pd dataframe for testing
    data0 = load_dataset(resume_files[0])
    data1 = load_dataset(resume_files[1])
    data2 = load_dataset(resume_files[2])
    
    # resumes are processed and cleaned
    resumes = process_datasets(resume_files)
    cleaned = fill_empty_fields(resumes)

    print(f"Total resumes loaded: {len(cleaned)}")
    
    n=2484+962
    print(f"Resume {n} sample:\n")
    pprint.pprint(cleaned[n])

    output_path = "cleaned_resumes.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)