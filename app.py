from flask import Flask, request, jsonify, render_template
import logging
from query_search import get_matching_jobs  
from response_generator import generate_response 

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route('/')
def home():
    """
    Render the home page.
    """
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_jobs():
    """
    Handle the search query and return job matches.
    """
    try:
        # Extract user query and optional parameters
        user_query = request.json.get('query', '')
        top_n = int(request.json.get('top_n', 3))

        if not user_query:
            return jsonify({"error": "Query is empty"}), 400

        logging.info(f"Received query: {user_query}")

        # Call RAG logic to get matching jobs
        result = get_matching_jobs(user_query, top_n)
        is_related_query = result["is_related"]

        if is_related_query:
            logging.info("Generating job summaries.")
            
            # Use a set to filter duplicates
            seen_job_ids = set()
            jobs_summary = "\n".join(
                f"{idx}. {meta.get('Business Title', 'N/A')}:\n"
                f"   Job ID: {meta.get('id', 'N/A')}\n"
                f"   Location: {meta.get('Work Location', 'N/A')}\n"
                f"   Description: {meta.get('Job Description', 'N/A')[:500]}...\n"
                f"   Preferred Skills: {meta.get('Preferred Skills', 'N/A')}\n"
                for idx, (_, meta) in enumerate(
                    [(score, meta) for score, meta in result["matches"] 
                     if meta.get("id") not in seen_job_ids and not seen_job_ids.add(meta.get("id"))],
                    start=1
                )
            )

            # Call LLM-based response generator
            response = generate_response(user_query, jobs_summary, query_type=is_related_query)
        else:
            logging.info("Query determined to be non-job-related.")
            response = generate_response(user_query, "", query_type=is_related_query)

        # Return formatted response
        print(response)
        return jsonify({
            # "is_related": is_related_query,
            "response": response,
          
        })

    except Exception as e:
        logging.error(f"Error processing query: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
