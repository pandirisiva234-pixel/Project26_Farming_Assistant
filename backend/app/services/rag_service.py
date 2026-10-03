import os

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PROJECT PATHS
# ============================================================

# This file is located at:
# Project26_Farming_Assistant/backend/app/services/rag_service.py
#
# Going up 3 levels gives:
# Project26_Farming_Assistant/backend

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


# Agricultural dataset location
DATASET_PATH = os.path.join(
    BASE_DIR,
    "..",
    "datasets",
    "farmerchat_andhra_pradesh.parquet"
)


# ChromaDB storage location
CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# CREATE CHROMADB CLIENT
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# ============================================================
# CREATE / GET COLLECTION
# ============================================================

collection = client.get_or_create_collection(
    name="farmerchat_ap"
)


# ============================================================
# LOAD AGRICULTURAL DOCUMENTS
# ============================================================

def load_documents():

    # Check whether dataset exists
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    # Read Parquet dataset
    df = pd.read_parquet(
        DATASET_PATH
    )

    documents = []
    metadatas = []
    ids = []

    # Process every farmer question
    for index, row in df.iterrows():

        query = str(row["query"])
        response = str(row["response"])
        crop = str(row["crop"])

        # Combine the important information
        document = (
            f"Crop: {crop}\n"
            f"Farmer Question: {query}\n"
            f"Answer: {response}"
        )

        documents.append(
            document
        )

        metadatas.append({
            "crop": crop
        })

        ids.append(
            f"farmerchat_{index}"
        )

    return (
        documents,
        metadatas,
        ids
    )


# ============================================================
# CREATE EMBEDDINGS AND STORE IN CHROMADB
# ============================================================

def create_embeddings():

    print("Loading agricultural dataset...")

    documents, metadatas, ids = load_documents()

    print(
        f"Loaded {len(documents)} agricultural documents."
    )

    print("Creating embeddings...")

    embeddings = model.encode(
        documents,
        show_progress_bar=True
    )

    print("Storing embeddings in ChromaDB...")

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print(
        f"Successfully stored {len(documents)} documents in ChromaDB."
    )

    return len(documents)


# ============================================================
# SEARCH AGRICULTURAL KNOWLEDGE
# ============================================================

def search_knowledge(
    query: str,
    top_k: int = 3
):

    query_embedding = model.encode(
        [query]
    )[0].tolist()

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=top_k
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    return documents


def extract_answer(document: str):

    if "Answer:" in document:
        answer = document.split(
            "Answer:",
            1
        )[1]

        return answer.strip()

    return document.strip()