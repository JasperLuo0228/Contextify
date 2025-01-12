from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import whisper
import tempfile
import os
import pandas as pd

from .audio_processing.audio_utils import process_audio
from .api_utils.gpt_utils import extract_entities_with_gpt
from .api_utils.gpt_utils_name import get_person_summary
from .api_utils.bing_utils import search_bing_news

app = FastAPI()
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading Whisper model...")
    global model
    model = whisper.load_model("small")
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

courses_df = pd.read_csv("app/All_Courses.csv")
def get_course_description(course_code: str) -> dict:
    course = courses_df[courses_df['Code'] == course_code]
    if not course.empty:
        return {
            "course_code": course_code,
            "course_name": course.iloc[0]['Name'],
            "description": course.iloc[0]['Description']
        }
    else:
        return {
            "course_code": course_code,
            "course_name": "Course not found",
            "description": "N/A"
        }

def get_person_description(person_name: str) -> dict:
    try:
        description = get_person_summary(person_name)
        return {
            "person_name": person_name,
            "description": description
        }
    except Exception as e:
        print(f"Error fetching description for {person_name}: {e}")
        return {
            "person_name": person_name,
            "description": "Could not fetch description for this person."
        }

def get_technical_term_definition(term: str) -> dict:
    return {
        "term": term,
        "description": "This is a placeholder definition for the technical term."
    }

def get_company_details(company_name: str) -> dict:
    api_key = os.getenv("BING_API_KEY")
    news = []

    try:
        result = search_bing_news(api_key=api_key, query=company_name, count=2)
        if "value" in result:
            for article in result["value"]:
                news.append({
                    "title": article.get("name", "No title"),
                    "summary": article.get("description", "No summary"),
                    "image_url": article.get("image", {}).get("thumbnail", {}).get("contentUrl", "No photo")
                })
        else:
            news.append({
                "title": "No news found",
                "summary": "No news summary available",
                "image_url": "No photo"
            })
    except Exception as e:
        print(f"Error fetching news: {e}")
        news.append({
            "title": "Error fetching news",
            "summary": str(e),
            "image_url": "No photo"
        })

    return {
        "company_name": company_name,
        "description": "This is a placeholder description for the company.",
        "news": news
    }

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_data = b""

    try:
        while True:
            chunk = await websocket.receive_bytes()
            print(f"Received audio chunk, size: {len(chunk)} bytes")
            audio_data += chunk

            if len(audio_data) > 1000000:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".raw") as raw_file:
                    raw_file.write(audio_data)
                    raw_file.flush()
                    raw_path = raw_file.name
                    print(f"[DEBUG] Temporary raw PCM file saved: {raw_path}")

                try:
                    wav_path = process_audio(raw_path)
                    print(f"[DEBUG] Converted raw PCM to WAV: {wav_path}")

                    result = model.transcribe(wav_path, fp16=False, language="en")
                    transcription = result["text"].strip()
                    print(f"[Whisper] Transcription: {transcription}")

                    extracted_entities = extract_entities_with_gpt(transcription)
                    print("[DEBUG] Extracted entities:", extracted_entities)

                    course_descriptions = [
                        get_course_description(course) for course in extracted_entities.get("Courses", [])
                    ]
                    person_descriptions = [
                        get_person_description(person) for person in extracted_entities.get("Names", [])
                    ]
                    technical_term_definitions = [
                        get_technical_term_definition(term) for term in extracted_entities.get("Technical terms", [])
                    ]
                    company_details = [
                        get_company_details(company) for company in extracted_entities.get("Companies", [])
                    ]

                    response_payload = {
                        "transcription": transcription,
                        "course_descriptions": course_descriptions,
                        "person_descriptions": person_descriptions,
                        "technical_term_definitions": technical_term_definitions,
                        "company_details": company_details
                    }

                    print("[DEBUG] Response payload:", response_payload)
                    await websocket.send_json(response_payload)

                finally:
                    audio_data = b""
                    os.remove(raw_path)
                    os.remove(wav_path)
                    print(f"[DEBUG] Cleaned up temporary files: {raw_path}, {wav_path}")
    except WebSocketDisconnect:
        print("WebSocket connection closed")