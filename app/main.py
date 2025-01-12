from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import whisper
import tempfile
import os

from .audio_processing.audio_utils import process_audio
from .api_utils.gpt_utils import extract_entities_with_gpt

app = FastAPI()
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading Whisper model...")
    global model
    model = whisper.load_model("base")
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

def get_course_description(course_code: str) -> dict:
    return {
        "course_code": course_code,
        "course_name": "Sample Course Name",
        "description": "This is a placeholder description for the course."
    }

def get_person_description(person_name: str) -> dict:
    return {
        "person_name": person_name,
        "description": "This is a placeholder description for the person."
    }

def get_technical_term_definition(term: str) -> dict:
    return {
        "term": term,
        "description": "This is a placeholder definition for the technical term."
    }

def get_company_details(company_name: str) -> dict:
    return {
        "company_name": company_name,
        "description": "This is a placeholder description for the company.",
        "news": [
            {
                "title": "Sample News Title 1",
                "summary": "This is a placeholder summary for news 1.",
                "image_url": "https://www.groovypost.com/wp-content/uploads/2015/08/rapa-valley-bing-feature.jpg"
            },
            {
                "title": "Sample News Title 2",
                "summary": "This is a placeholder summary for news 2.",
                "image_url": "https://www.groovypost.com/wp-content/uploads/2015/08/rapa-valley-bing-feature.jpg"
            }
        ]
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
                    #os.remove(wav_path)
                    print(f"[DEBUG] Cleaned up temporary files: {raw_path}, {wav_path}")
    except WebSocketDisconnect:
        print("WebSocket connection closed")