from flask import Flask, request, render_template
import fitz  # PyMuPDF for PDF parsing
import spacy
import openai
import os

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Initialize Flask app
app = Flask(__name__)

# Create 'uploads' folder if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')


# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text


# Match resume text with job description (keywords matching)
def match_keywords(resume_text, job_desc):
    resume_doc = nlp(resume_text.lower())
    job_doc = nlp(job_desc.lower())
    common_words = set(token.text for token in resume_doc) & set(token.text for token in job_doc)
    return common_words


# Get AI-based suggestions for improvement using OpenAI
def analyze_resume(resume_text):
    prompt = f"Analyze this resume and provide suggestions for improvement:\n{resume_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]


# Route for file upload and resume analysis
@app.route("/", methods=["GET", "POST"])
def upload_file():
    print("Received request for upload page")  # Debugging log
    if request.method == "POST":
        print("POST request received")  # Debugging log
        file = request.files["file"]
        if file and file.filename.endswith(".pdf"):
            file_path = "uploads/" + file.filename
            file.save(file_path)
            print(f"File saved: {file_path}")  # Debugging log

            # Extract resume text
            resume_text = extract_text_from_pdf(file_path)
            print(f"Extracted resume text: {resume_text[:100]}...")  # Debugging log (only print the first 100 chars)

            # Example job description (this can be dynamic or input from user)
            job_desc = "Looking for a Python Developer with Django and AI/ML skills."

            # Match keywords with job description
            matched_skills = match_keywords(resume_text, job_desc)
            print(f"Matched skills: {matched_skills}")  # Debugging log

            # Get AI-based suggestions for improvement
            resume_feedback = analyze_resume(resume_text)
            print(f"Resume feedback: {resume_feedback}")  # Debugging log

            # Return results to user
            return render_template("result.html", resume_text=resume_text, matched_skills=matched_skills,
                                   resume_feedback=resume_feedback)

    return '''
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload Resume">
    </form>
    '''


if __name__ == "__main__":
    app.run(debug=True)