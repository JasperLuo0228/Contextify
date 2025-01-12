from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import whisper
import asyncio
import tempfile
import os

from .audio_processing.audio_utils import process_audio

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

                try:
                    print(f"[DEBUG] Converting raw PCM to WAV: {raw_path}...")
                    wav_path = process_audio(raw_path)

                    print(f"[DEBUG] Transcribing WAV: {wav_path}...")
                    result = model.transcribe(wav_path, fp16=False, language="en")
                    transcription = result["text"].strip()
                    print(f"[Whisper] {transcription}")
                    
                    await websocket.send_json({
                        "transcription": transcription,
                        # "entities":
                    })

                finally:
                    audio_data = b""
                    os.remove(raw_path)
                    os.remove(wav_path)
    except WebSocketDisconnect:
        print("WebSocket connection closed")
