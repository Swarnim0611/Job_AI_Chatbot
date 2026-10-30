import faiss
import numpy as np
import pickle
import os
import logging
from response_generator import generate_response
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from logger_config import setup_logger

# Configure logging
setup_logger()
load_dotenv()

# Load environment variables
EMBEDDING_IDX_PATH = os.getenv("IDX_FILE_PATH")
METADATA_OUTPUT_PATH = os.getenv("METADATA_OUTPUT_PATH")
MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.5))  
NON_JOB_THRESHOLD = float(os.getenv("NON_JOB_THRESHOLD", 0.2))  

# Initialize the embedding model
model = SentenceTransformer(MODEL_NAME)

def load_index_and_metadata():
    """
    Load the Faiss index and metadata.

    Returns:
        faiss.IndexFlatL2: Loaded Faiss index.
        list: Metadata corresponding to embeddings.
    """
    try:
        if not os.path.exists(EMBEDDING_IDX_PATH):
            raise FileNotFoundError(f"Embedding index file not found at: {EMBEDDING_IDX_PATH}")
        if not os.path.exists(METADATA_OUTPUT_PATH):
            raise FileNotFoundError(f"Metadata file not found at: {METADATA_OUTPUT_PATH}")

        # Load Faiss index
        logging.info(f"Loading Faiss index from: {EMBEDDING_IDX_PATH}")
        index = faiss.read_index(EMBEDDING_IDX_PATH)
        print("Number of embeddings in index:", index.ntotal)

        # Load metadata
        logging.info(f"Loading metadata from: {METADATA_OUTPUT_PATH}")
        with open(METADATA_OUTPUT_PATH, "rb") as f:
            metadata = pickle.load(f)
            print("Number of metadata entries:", len(metadata))

        return index, metadata
    except Exception as e:
        logging.error(f"Error loading index and metadata: {e}", exc_info=True)
        raise

def get_query_embedding(query):
    """
    Generate an embedding for the query using sentence or token-level embeddings.

    Args:
        query (str): Input query.

    Returns:
        np.ndarray: Query embedding.
    """
    words = query.split()  
    if len(words) > 5: 
        logging.info("Using token-level embedding for the query.")
        word_embeddings = model.encode(words, show_progress_bar=False).astype("float32")
        query_embedding = np.mean(word_embeddings, axis=0)
    else:  
        logging.info("Using sentence-level embedding for the query.")
        query_embedding = model.encode(query).astype("float32")
    return query_embedding

def get_matching_jobs(query, top_n=3):
    """
    Retrieve the top job matches for the given query using Faiss index.

    Args:
        query (str): User's input query.
        top_n (int): Number of top matches to return.
    
    Returns:
        dict: Contains `is_related` flag, matching job metadata, and similarity scores.
    """
    try:
        logging.info(f"Processing query: {query}")

        # Step 1: Load Faiss index and metadata
        index, metadata = load_index_and_metadata()

        # Step 2: Generate query embedding
        logging.info("Generating embedding for the query.")
        query_embedding = get_query_embedding(query)

        # Step 3: Search for nearest neighbors in the index
        logging.info("Performing similarity search.")
        distances, indices = index.search(np.array([query_embedding]), top_n)

        # Step 4: Debug distances and indices
        logging.debug(f"Distances: {distances}")
        logging.debug(f"Indices: {indices}")

        # Step 5: Convert distances to similarities and filter results
        matches = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:  # Ensure valid index
                similarity = 1 - dist  # Convert distance to similarity
                if similarity > SIMILARITY_THRESHOLD:
                    matches.append((similarity, metadata[idx]))
        

        if not matches:
            logging.warning("No matches found above the similarity threshold.")
        else:
            logging.info(f"Found {len(matches)} matches above the threshold.")

        # Step 6: Determine if query is job-related
        is_related = len(matches) > 0
        context = f"Found {len(matches)} matching jobs for your query." if is_related else "This query is not related to jobs."
        return {"is_related": is_related, "matches": matches, "context": context}

    except Exception as e:
        logging.error(f"Error in job matching: {e}", exc_info=True)
        return {"is_related": False, "matches": [], "context": "An error occurred during query processing."}

