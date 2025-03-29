from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from fpdf import FPDF
import google.generativeai as genai
import os

# Read API Key from environment variable
API_KEY = os.getenv('API_KEY')

genai.configure(api_key=API_KEY)

app = Flask(__name__)
CORS(app)

# PDF Generation Class
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", size=12)
        self.cell(0, 10, "Travel Itinerary", align="C", ln=1)

    def add_day(self, day, content):
        self.set_font("Arial", style="B", size=12)
        self.cell(0, 10, f"{day}", ln=1)
        self.set_font("Arial", size=12)
        self.multi_cell(0, 10, content)
        self.ln(5)  # Add space after each day's itinerary

# Function to generate itinerary in plain text format
def generate_itinerary(source, destination, duration, budget, preferences):
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # Enforcing plain text response with structured day-wise format
    prompt = (
        f"Generate a detailed {duration}-day travel itinerary from {source} to {destination} "
        f"with a budget of Rs. {budget}. Preferences: {preferences}. "
        f"Format the itinerary with 'Day X:' followed by activities for each day. "
        f"Use plain text and avoid Markdown or bullet points."
    )

    response = model.generate_content([prompt])
    
    # Convert Markdown-like response to plain text format
    itinerary_text = response.text.replace("*", "").replace("#", "").replace("-", "").strip()
    
    return itinerary_text

# Function to save itinerary to a PDF file
def save_to_pdf(text):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Replace ₹ with Rs. in the generated text before saving to PDF
    text = text.replace("₹", "Rs.")
    
    # Split text into days and add each to the PDF
    lines = text.split("\n")
    for line in lines:
        if line.startswith("Day "):  # Detecting day headers
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(0, 10, line, ln=1)
            pdf.set_font("Arial", size=12)
        else:
            pdf.multi_cell(0, 10, line)

    pdf.output("itinerary.pdf")
    return "itinerary.pdf"

@app.route('/generate_itinerary', methods=['POST'])
def generate_itinerary_api():
    data = request.json
    
    source = data.get("source", "")
    destination = data.get("destination", "")
    duration = data.get("duration", "")
    budget = data.get("budget", "")
    preferences = data.get("preferences", "")

    itinerary_text = generate_itinerary(source, destination, duration, budget, preferences)
    
    # Save to PDF
    pdf_path = save_to_pdf(itinerary_text)
    
    return jsonify({"itinerary_text": itinerary_text, "pdf_path": pdf_path})

@app.route('/download_pdf')
def download_pdf():
    return send_file("itinerary.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
