import requests
import logging
from dotenv import load_dotenv
from logger_config import setup_logger
import json

# Configure logging
setup_logger()

load_dotenv()


OLLAMA_API_URL = "http://localhost:11434/api/generate"

def generate_response(user_query, jobs_summary, query_type):
    """
    Generate a response using the LLaMA 2 model based on the user's query and matching results.

    Args:
        user_query (str): The user's query.
        jobs_summary (str): Formatted string containing job summaries or an empty string for non-job-related queries.
        query_type (bool): Indicates whether the query is job-related or not.

    Returns:
        str: The generated response from the LLM.
    """
    try:
        # Step 1: Deduplicate job summaries
        def deduplicate_jobs(summary):
            seen_jobs = set()
            deduplicated_summary = []
            for line in summary.split("\n\n"):  
                job_id_line = next((part for part in line.split("\n") if "Job ID:" in part), None)
                if job_id_line and job_id_line not in seen_jobs:
                    seen_jobs.add(job_id_line)
                    deduplicated_summary.append(line.strip())
            return "\n\n".join(deduplicated_summary)

        # Deduplicate the jobs summary
        jobs_summary = deduplicate_jobs(jobs_summary)

        # Step 2: Construct the prompt
        if query_type:  # Job-related query
            prompt = f"""
            You are an intelligent assistant helping users find job opportunities.
            The user asked: "{user_query}"
            
            Here are the matching job opportunities:
            {jobs_summary}

            Please summarize the top results concisely. Avoid repetition, and ensure each job description is unique. 
            Highlight the most relevant roles based on the user's skills and provide encouragement to explore further. 
            Format the response as a numbered list with bullet points for details. 
            Use markdown formatting for clarity.
            """
        else:  # Non-job-related query
            prompt = f"""
            You are a domain-specific assistant for job-related queries. The user asked: "{user_query}"
            
            This query is not related to job opportunities. Respond warmly and professionally, 
            offering help if the user has questions about jobs or other topics. Use concise and polite language
            Use actual emojis where appropriate, and avoid adding any unnecessary phrases like "Here is my response" or "Of course."
            Do not use emojis unnecessarily.
            If user greets 'hi' or 'hello' or 'thanks' or 'thank you' then response warmly and avoid using unnecessary information or explanation.
            """

        # Step 3: Send the request to the Ollama LLaMA 2 API
        payload = {
            "model": "llama2",
            "prompt": prompt,
            "max_tokens": 200
        }
        logging.debug(f"Sending payload to Ollama API: {payload}")

        response = requests.post(OLLAMA_API_URL, json=payload, stream=True)

        if response.status_code == 200:
            aggregated_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():  # Ignore empty lines
                    try:
                        # Parse each line as JSON
                        json_line = json.loads(line)
                        aggregated_response += json_line.get("response", "")
                        # Stop if "done" is True
                        if json_line.get("done", False):
                            break
                    except json.JSONDecodeError as e:
                        logging.warning(f"Failed to parse line as JSON: {line}")
            
            # Ensure the response is clean and non-empty
            return aggregated_response.strip() or "I'm sorry, I couldn't generate a response at this time."
        else:
            # Log API response error details
            logging.error(f"Ollama API returned an error: {response.status_code}, {response.text}")
            return "There was an error generating the response. Please try again later."

    except Exception as e:
        logging.error(f"Error in generating response: {e}", exc_info=True)
        return "An error occurred while generating the response. Please try again later."
