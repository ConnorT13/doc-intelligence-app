# this is the backend for a dummy document ai application
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
# Configure OpenAI key here or through environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# enable CORS, lets frontend talk to backend 
#the "*" means "allow all origins" fine for development, not for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract/")
async def extract_from_pdf(file: UploadFile = File(...)):
    # extract pdf
    with pdfplumber.open(file.file) as pdf:
        full_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    prompt = f"""
    Extract the structured JSON from this invoice, Includ fields like buyer name, address, date, and a list of items with name quantity, and price.PermissionError

    Document Text:
    {full_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}