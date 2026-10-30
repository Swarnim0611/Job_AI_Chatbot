import pandas as pd
import os
import logging
from dotenv import load_dotenv
from logger_config import setup_logger


#configure logs
setup_logger()

# Load environment variables
load_dotenv()

def load_and_clean_data(input_path: str, output_path: str):
    """
    Load and preprocess the job data.

    Args:
        input_path (str): Path to the raw CSV file.
        output_path (str): Path to save the cleaned CSV file.
    
    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    try:
        if os.path.exists(output_path):
            logging.info("Cleaned data already exists. Loading it.")
            return pd.read_csv(output_path)

        logging.info("Loading raw data.")
        df = pd.read_csv(input_path)

        # Log initial data size and columns
        logging.info(f"Initial data size: {df.shape}")
        logging.info(f"Columns in dataset: {list(df.columns)}")

        # Drop unnecessary columns
        columns_to_drop = [
            'Civil Service Title', 'Title Classification', 'Title Code No',
            'Level', 'Salary Frequency', 'Additional Information',
            'Residency Requirement', 'Posting Date', 'Post Until',
            'Posting Updated', 'Process Date'
        ]
        df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
        logging.info(f"Columns after dropping unnecessary ones: {list(df.columns)}")

        # Remove duplicates
        initial_rows = df.shape[0]
        df.drop_duplicates(inplace=True)
        logging.info(f"Duplicates removed. Rows reduced from {initial_rows} to {df.shape[0]}.")

        # Remove rows with NaN in critical columns
        critical_columns = ['Job ID', 'Job Description']  # Ensure these columns are not empty
        df.dropna(subset=critical_columns, inplace=True)
        logging.info(f"Rows after dropping NaN in critical columns: {df.shape[0]}")

        # Strip whitespace in text columns
        text_columns = ['Job Description', 'Minimum Qual Requirements', 'Preferred Skills']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Check if DataFrame is empty
        if df.empty:
            logging.warning("No data available after cleaning. Exiting...")
            print("Warning: The cleaned DataFrame is empty. No data saved.")
            return

        # Save cleaned data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        logging.info(f"Cleaned data saved successfully to: {output_path}")

        return df
    except Exception as e:
        logging.error(f"Error during data preprocessing: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        raw_data_path = os.getenv("RAW_DATA_PATH")
        cleaned_data_path = os.getenv("CLEANED_DATA_PATH")

        # Validate paths from .env file
        if not raw_data_path or not cleaned_data_path:
            raise ValueError("Missing required paths in the .env file.")

        load_and_clean_data(raw_data_path, cleaned_data_path)
    except Exception as e:
        logging.critical(f"Critical error in data preprocessing: {str(e)}")
