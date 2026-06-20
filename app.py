"""
Rush transcription server — on-device-free speech-to-text using faster-whisper.

Receives an audio file (m4a/mp3/wav/ogg), returns the recognized text as JSON.
No API keys needed; the Whisper model runs locally on the server.

Endpoints:
  GET  /            → health check (also wakes a sleeping free host)
  POST /transcribe  → multipart form-data, field "file" = audio; optional "lang" (ru/en/auto)
"""

import os
import tempfile

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel

# ── Model configuration ──────────────────────────────────────────────────────
# "small" is the sweet spot for free CPU hosting: decent accuracy, ~460MB, runs
# in a few seconds per voice message. Use "base" or "tiny" if the host is too
# slow / runs out of memory; "medium" is more accurate but heavy.
MODEL_SIZE = os.environ.get("WHISPER_MODEL", "small")

# int8 quantization keeps CPU memory low and speeds inference on free tiers.
print(f"[startup] loading faster-whisper model '{MODEL_SIZE}' (int8, cpu)...")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
print("[startup] model loaded, server ready")

app = FastAPI(title="Rush Transcribe")

# Allow the mobile app (and web) to call from anywhere.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    # Hitting this also wakes the free host if it was asleep.
    return {"ok": True, "model": MODEL_SIZE}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), lang: str = Form("auto")):
    # Save the uploaded audio to a temp file (faster-whisper reads from a path).
    suffix = os.path.splitext(file.filename or "")[1] or ".m4a"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"upload failed: {e}")

    try:
        # language=None lets Whisper auto-detect; otherwise force ru/en.
        language = None if lang in ("auto", "", None) else lang
        segments, info = model.transcribe(
            tmp_path,
            language=language,
            vad_filter=True,            # skip silence → faster, cleaner
            beam_size=1,                # fastest decoding for short clips
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return {
            "text": text or "",
            "language": info.language,
            "duration": round(info.duration, 1),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"transcription failed: {e}")
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
