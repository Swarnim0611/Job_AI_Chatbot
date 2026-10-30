import pandas as pd
import numpy as np
import os
import faiss
import pickle
import logging
from typing import Optional
from dotenv import load_dotenv
from logger_config import setup_logger

#configure logs
setup_logger()

# Load environment variables
load_dotenv()

def save_embeddings_to_files(
    csv_embeddings_path: str,
    idx_file_path: str,
    embedding_dim: Optional[int] = None,
):
    """
    Reads embedded CSV data and saves it as .idx and .pkl files.

    Args:
        csv_embeddings_path (str): Path to the CSV file containing embeddings.
        idx_file_path (str): Path to save the .idx file (FAISS index).
        pkl_file_path (str): Path to save the .pkl file (pickle serialized embeddings).
        embedding_dim (int, optional): Dimensionality of embeddings (optional if inferable).
    """
    try:
        # Load embeddings from CSV
        logging.info(f"Loading embeddings from: {csv_embeddings_path}")
        embeddings_df = pd.read_csv(csv_embeddings_path)
        logging.info(f"Loaded embeddings with shape: {embeddings_df.shape}")

        # Convert to NumPy array
        embeddings = embeddings_df.to_numpy(dtype=np.float32)

        # Infer embedding dimension if not provided
        if embedding_dim is None:
            embedding_dim = embeddings.shape[1]
        logging.info(f"Inferred embedding dimension: {embedding_dim}")

        # Create and save FAISS index (.idx file)
        logging.info("Creating FAISS index.")
        index = faiss.IndexFlatL2(embedding_dim)  # L2 (Euclidean distance)
        index.add(embeddings)  # Add embeddings to the index
        logging.info(f"Saving FAISS index to .idx file: {idx_file_path}")
        faiss.write_index(index, idx_file_path)
        logging.info(".idx file saved successfully.")

    except Exception as e:
        logging.error(f"Error during embeddings conversion: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        # Define file paths
        csv_embeddings_path = os.getenv("CSV_EMBEDDINGS") # Input embedded CSV
        idx_file_path = os.getenv("IDX_FILE_PATH")  # Output .idx file

        # Call the function to save embeddings
        save_embeddings_to_files(csv_embeddings_path, idx_file_path)

        logging.info("Embedding conversion completed successfully.")

    except Exception as e:
        logging.critical(f"Critical error: {str(e)}", exc_info=True)

