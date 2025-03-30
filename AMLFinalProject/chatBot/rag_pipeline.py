# import json
# import pandas as pd
# from tqdm import tqdm
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain.docstore.document import Document
# from langchain.chains import RetrievalQA
# from langchain_ollama.llms import OllamaLLM

# # Load JSON data into a pandas DataFrame
# with open("./chatBot/cleaned_resumes_actual.json", "r") as f:
#     data = json.load(f)
# df = pd.DataFrame(data)  # Assuming the JSON is a list of dictionaries

# # Instantiate the embeddings model using all‑MiniLM‑L6‑v2
# embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# # Process each resume into a Document object with a progress bar
# documents = []
# for _, row in tqdm(df.iterrows(), total=len(df), desc="Preparing documents"):
#     text = row['resume']
#     #metadata = {"id": row['ID'], "category": row['Category']}
#     metadata = {"summary": row['summary'], "skills": row['skills'],
#                 "position": row['position'], "education": row['education'],
#                 "major": row['major'], "educational_records": row['educational_records'],
#                 "result_type": row['result_type'], "graduation_year": row['graduation_year'],
#                 "certifications": row['certifications'], "projects": row['projects'],
#                 "languages": row['languages'], "meta": row['meta'],}
#     documents.append(Document(page_content=text, metadata=metadata))

# # Define a directory to persist the Chroma DB vector store
# persist_directory = "./chroma_db_resume"

# # Create the vector store from the documents using the HuggingFace embeddings
# vectorstore = Chroma.from_documents(documents, embedding_model, persist_directory=persist_directory)
# vectorstore.persist()

# print("Embeddings generated and stored in Chroma DB using all‑MiniLM‑L6‑v2 HuggingFace Embeddings.")

# # Instantiate the Ollama LLM (ensure your local Ollama server is accessible at the provided base_url)
# llm = OllamaLLM(model="llama3.2", base_url="http://127.0.0.1:11434/")  

# # Create a RetrievalQA chain using the vectorstore as the retriever.
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff",
#     retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
# )

# print("RetrievalQA chain is set up and ready for queries using Ollama LLM.")


import json
import pandas as pd
from tqdm import tqdm
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain_ollama.llms import OllamaLLM

def process_metadata_value(value):
    """
    Convert metadata values to acceptable types.
    If it's a list, join its elements into a string.
    If it's a dict, convert it to a JSON string.
    Otherwise, return the value as is.
    """
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    elif isinstance(value, dict):
        return json.dumps(value)
    else:
        return value

# Load JSON data into a pandas DataFrame
with open("./chatBot/cleaned_resumes_actual.json", "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)  # Assuming the JSON is a list of dictionaries

# Instantiate the embeddings model using all‑MiniLM‑L6‑v2
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Process each resume into a Document object with a progress bar
documents = []
# List of keys to process from the JSON as metadata
metadata_fields = [
    "summary", "skills", "position", "education", "major", 
    "educational_records", "result_type", "graduation_year", 
    "certifications", "projects", "languages", "meta"
]

for _, row in tqdm(df.iterrows(), total=len(df), desc="Preparing documents"):
    text = row['resume']
    metadata = {}
    for field in metadata_fields:
        # Use .get() in case some fields are missing
        metadata[field] = process_metadata_value(row.get(field, ""))
    documents.append(Document(page_content=text, metadata=metadata))

# Define a directory to persist the Chroma DB vector store
persist_directory = "./chroma_db_resume"

# Create the vector store from the documents using the HuggingFace embeddings
vectorstore = Chroma.from_documents(documents, embedding_model, persist_directory=persist_directory)
vectorstore.persist()

print("Embeddings generated and stored in Chroma DB using all‑MiniLM‑L6‑v2 HuggingFace Embeddings.")

# Instantiate the Ollama LLM (ensure your local Ollama server is accessible at the provided base_url)
llm = OllamaLLM(model="llama3.2", base_url="http://127.0.0.1:11434/")

# Create a RetrievalQA chain using the vectorstore as the retriever.
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
)

print("RetrievalQA chain is set up and ready for queries using Ollama LLM.")
