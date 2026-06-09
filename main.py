from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai
from fastapi import UploadFile, File
from pypdf import PdfReader
from PIL import Image
import shutil
import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import time
import json


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)
print("\nAVAILABLE GEMINI MODELS:\n")

for model in genai.list_models():
    print(model.name)

vision_model = genai.GenerativeModel(
    "gemini-2.5-flash"
)
PDF_CONTENT = ""
with open("system_prompt.txt", "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()

print(SYSTEM_PROMPT)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "Backend is running"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    try:

        prompt = f"""
{SYSTEM_PROMPT}

User: {request.message}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response.choices[0].message.content

        return {
            "response": answer
        }

    except Exception as e:

        return {
            "response": f"Error: {str(e)}"
        }
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "saved_to": file_path,
        "message": "Image saved successfully"
    }
@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):

    try:

        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image = Image.open(file_path)

        response = vision_model.generate_content(
            [
                "Describe this image in detail.",
                image
            ]
        )

        return {
            "response": response.text
        }

    except Exception as e:

        return {
            "response": str(e)
        }
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    global PDF_CONTENT

    try:

        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        reader = PdfReader(file_path)

        pdf_text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                pdf_text += page_text + "\n"

        PDF_CONTENT = pdf_text

        return {
            "filename": file.filename,
            "text": pdf_text[:5000]
        }

    except Exception as e:

        return {
            "error": str(e)
        }
@app.post("/ask-pdf")
def ask_pdf(request: ChatRequest):

    global PDF_CONTENT

    try:

        prompt = f"""
        You are analyzing a PDF.

        PDF Content:
        {PDF_CONTENT}

        User Question:
        {request.message}

        Answer only using information from the PDF.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return {
            "response":
            response.choices[0].message.content
        }

    except Exception as e:

        return {
            "response": str(e)
        }
@app.post("/stream")
async def stream(request: Request):

    data = await request.json()
    message = data.get("message", "")

    # fake AI response (replace with Gemini/Groq later)
    response = f"Hello! You asked: {message}. I am Mukesh AI streaming response."

    def generate():
        for word in response.split():
            yield word + " "
            time.sleep(0.15)

    return StreamingResponse(generate(), media_type="text/plain")