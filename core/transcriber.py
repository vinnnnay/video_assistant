import whisper
import os
import requests
import time
from pydub import AudioSegment

# Sarvam's sync STT-translate API rejects audio longer than 30s.
# We slice each chunk into 25s pieces (with a 5s safety margin) before sending.
SARVAM_PIECE_SECONDS = 25
SARVAM_MAX_RETRIES = 3
SARVAM_BACKOFF_BASE_SECONDS = 2
SARVAM_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}


WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")


SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

_model = None


def load_model():

    global _model  

    if _model is None: 
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = whisper.load_model(WHISPER_MODEL) 
        print("Whisper model loaded.")
    return _model 


def transcribe_chunk_whisper(chunk_path: str) -> str:

    model = load_model()  

    result = model.transcribe(chunk_path, task="transcribe")  
    return result["text"]  


def _send_to_sarvam(piece_path: str) -> str:
    """Send one ≤30s WAV file to Sarvam and return the English transcript."""
    headers = {"api-subscription-key": SARVAM_API_KEY}
    response = None

    for attempt in range(1, SARVAM_MAX_RETRIES + 1):
        with open(piece_path, "rb") as f:
            files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
            data = {"model": SARVAM_MODEL, "with_diarization": "false"}
            try:
                response = requests.post(
                    SARVAM_STT_TRANSLATE_URL,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=120,
                )
            except requests.RequestException as exc:
                if attempt == SARVAM_MAX_RETRIES:
                    raise RuntimeError(
                        f"Sarvam request failed after {SARVAM_MAX_RETRIES} attempts: {exc}"
                    ) from exc
                backoff = SARVAM_BACKOFF_BASE_SECONDS ** (attempt - 1)
                print(
                    f"  ⚠️ Sarvam request failed on attempt {attempt}/{SARVAM_MAX_RETRIES}: {exc}. Retrying in {backoff}s..."
                )
                time.sleep(backoff)
                continue

        if response.ok:
            return response.json().get("transcript", "")

        if response.status_code in SARVAM_RETRY_STATUS_CODES:
            if attempt == SARVAM_MAX_RETRIES:
                break
            backoff = SARVAM_BACKOFF_BASE_SECONDS ** (attempt - 1)
            print(
                f"  ⚠️ Sarvam returned {response.status_code} on attempt {attempt}/{SARVAM_MAX_RETRIES}. Retrying in {backoff}s..."
            )
            time.sleep(backoff)
            continue

        print(f"\n❌ Sarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    raise RuntimeError(
        f"Sarvam API unavailable after {SARVAM_MAX_RETRIES} attempts: {response.status_code} {response.text}"
    )


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API only accepts ≤30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_sarvam(piece_path) + " "
        except RuntimeError as exc:
            print(f"\n❌ Sarvam piece {i + 1}/{total_pieces} failed: {exc}")
            print("  Falling back to local Whisper transcription for this chunk.")
            return transcribe_chunk_whisper(chunk_path)
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()

   



def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route one chunk to Whisper or Sarvam depending on language choice.
    - english  → Whisper (local model)
    - hinglish → Sarvam (translates to English while transcribing)
    """
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)


def transcribe_all(chunks: list, language: str = "english") -> str:

    full_transcript = "" 

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
    print(f"Using {engine} for transcription.")

    for i, chunk in enumerate(chunks):  

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(chunk, language=language)  

        full_transcript += text + " "  

    print("Transcription complete.")

    return full_transcript.strip()  