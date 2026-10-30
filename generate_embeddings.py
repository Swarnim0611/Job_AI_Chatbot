import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
import logging
from dotenv import load_dotenv
from logger_config import setup_logger

# Configure logging
setup_logger()

# Load environment variables
load_dotenv()

# Fetch paths from .env file
CLEANED_DATA_PATH = os.getenv("CLEANED_DATA_PATH", "data/cleaned.csv")
EMBEDDINGS_OUTPUT_PATH = os.getenv("EMBEDDINGS_OUTPUT_PATH", "data/embedded_output.csv")
METADATA_OUTPUT_PATH = os.getenv("METADATA_OUTPUT_PATH", "data/metadata.pkl")

# Initialize the embedding model
MODEL_NAME = os.getenv("MODEL_NAME", "msmarco-distilbert-base-v4")
model = SentenceTransformer(MODEL_NAME)

def chunk_text(text, max_chunk_size=150):
    """
    Splits text into smaller chunks based on the max_chunk_size.

    Args:
        text (str): The text to be chunked.
        max_chunk_size (int): Maximum number of characters per chunk.

    Returns:
        List[str]: List of text chunks.
    """
    return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

def generate_embeddings():
    """
    Generate embeddings for the cleaned job data and save them to CSV and metadata to a pickle file.

    Returns:
        Tuple[np.ndarray, List[dict]]: Generated embeddings and metadata.
    """
    try:
        logging.info("Starting the embedding generation process.")
        
        # Load cleaned data
        if not os.path.exists(CLEANED_DATA_PATH):
            logging.error(f"Cleaned data not found at: {CLEANED_DATA_PATH}")
            raise FileNotFoundError(f"Cleaned data not found at: {CLEANED_DATA_PATH}")
        
        logging.info(f"Loading cleaned data from: {CLEANED_DATA_PATH}")
        data = pd.read_csv(CLEANED_DATA_PATH)

        # Initialize embedding and metadata containers
        embeddings = []
        metadata = []

        # Process each row for embeddings
        logging.info("Processing rows for embedding generation.")
        for index, row in data.iterrows():
            row_embeddings = []
            row_metadata = {"id": row.get("Job ID", index)}  # Default ID is the index if 'Job ID' is missing
            
            # Iterate over relevant columns for embedding generation
            for col in ["Business Title", "Job Category", "Work Location", "Job Description", "Minimum Qual Requirements", "Preferred Skills"]:
                if pd.notnull(row.get(col)):  # Skip if column data is null
                    text_chunks = chunk_text(row[col])
                    chunk_embeddings = []

                    # Generate embeddings for each chunk
                    for chunk in text_chunks:
                        embedding = model.encode(chunk).astype("float32")
                        embedding = embedding / np.linalg.norm(embedding)  # Normalize
                        chunk_embeddings.append(embedding)

                    # Combine chunk embeddings (mean pooling)
                    if chunk_embeddings:
                        col_embedding = np.mean(chunk_embeddings, axis=0)
                        row_embeddings.append(col_embedding)
                        row_metadata[col] = row[col]

            # Combine row embeddings (mean pooling) and store metadata
            if row_embeddings:
                combined_embedding = np.mean(row_embeddings, axis=0)
                embeddings.append(combined_embedding)
                metadata.append(row_metadata)

        # Convert embeddings to a DataFrame and save to CSV
        embedding_df = pd.DataFrame(embeddings)
        os.makedirs(os.path.dirname(EMBEDDINGS_OUTPUT_PATH), exist_ok=True)
        embedding_df.to_csv(EMBEDDINGS_OUTPUT_PATH, index=False)
        logging.info(f"Embeddings saved to: {EMBEDDINGS_OUTPUT_PATH}")

        # Save metadata to a pickle file
        with open(METADATA_OUTPUT_PATH, "wb") as f:
            pickle.dump(metadata, f)
        logging.info(f"Metadata saved to: {METADATA_OUTPUT_PATH}")

        logging.info("Embedding generation completed successfully.")
        return embeddings, metadata

    except Exception as e:
        logging.error(f"Error during embedding generation: {e}", exc_info=True)
        raise
 
if __name__ == "__main__":
    try:
        logging.info("Starting the embedding generation script.")
        generate_embeddings()
        logging.info("Script completed successfully.")
    except Exception as e:
        logging.critical(f"Critical error in embedding generation script: {e}", exc_info=True)
