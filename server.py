import base64
import os
from google import genai
from google.genai import types
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__, static_folder='.', static_url_path='')  # Serve static files from the current directory

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')  # Serve the index.html file

@app.route('/api/gemini', methods=['POST'])
def generate_gemini_response():
    prompt_text = request.json.get('prompt')
    if not prompt_text:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),  # API key from environment variable
        )

        model = "gemini-2.0-flash-lite"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt_text),  # Use the prompt from the request
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
            system_instruction=types.Part.from_text(text="""You are a revision-focused teacher bot designed to help Key Stage 3, Year 9 pupils in the UK prepare for assessments. You will explain topics and provide revision materials based on prompts, videos, and websites, with a focus on Save My Exams.

Your responses should include:

* Clear explanations of key concepts.
* Summaries of important information.
* Practice questions and answers.
* Links to relevant revision resources, especially from Save My Exams.
* Tips for exam technique and time management.
* A focus on common misconceptions and how to avoid them.
* If the subject is mathematics or science, use LaTeX to display equations and formulas.
* If provided with a video or web page, provide a concise summary of the content.
* Identify key vocabulary.

Your aim is to help pupils achieve their best possible grades."""),
        )

        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if hasattr(chunk, 'text'):  # Ensure the chunk has a 'text' attribute
                response_text += chunk.text

        return jsonify({"response": response_text}), 200  # Return the response text as JSON

    except Exception as e:
        print(f"Error generating content: {e}")
        return jsonify({"error": f"Failed to generate response: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Run the Flask app on port 5000