import json
import pandas as pd
from tqdm import tqdm
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain_ollama.llms import OllamaLLM

# Load JSON data into a pandas DataFrame
with open("./chatBot/cleaned_resumes.json", "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)  # Assuming the JSON is a list of dictionaries

# Instantiate the embeddings model using all‑MiniLM‑L6‑v2
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Process each resume into a Document object with a progress bar
documents = []
for _, row in tqdm(df.iterrows(), total=len(df), desc="Preparing documents"):
    text = row['Clean_resume']
    #metadata = {"id": row['ID'], "category": row['Category']}
    metadata = {"id": row['ID']}
    documents.append(Document(page_content=text, metadata=metadata))

# Define a directory to persist the Chroma DB vector store
persist_directory = "./chroma_db_resume"

# Create the vector store from the documents using the HuggingFace embeddings
vectorstore = Chroma.from_documents(documents, embedding_model, persist_directory=persist_directory)
vectorstore.persist()

print("Embeddings generated and stored in Chroma DB using all‑MiniLM‑L6‑v2 HuggingFace Embeddings.")

# Instantiate the Ollama LLM (ensure your local Ollama server is accessible at the provided base_url)
llm = OllamaLLM(model="phi4", base_url="http://10.50.10.240:10023/")  

# Create a RetrievalQA chain using the vectorstore as the retriever.
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
)

print("RetrievalQA chain is set up and ready for queries using Ollama LLM.")
