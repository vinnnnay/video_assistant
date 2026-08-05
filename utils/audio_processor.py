import glob
import os
import shutil
from pydub import AudioSegment
import yt_dlp

DOWNLOAD_DIR = "downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def find_ffmpeg_location() -> str | None:
    env_path = os.environ.get("FFMPEG_PATH")
    if env_path:
        env_path = env_path.strip(' "\'')
        if os.path.isfile(env_path):
            return os.path.dirname(env_path)
        if os.path.isdir(env_path):
            return env_path

    for exe in ("ffmpeg.exe", "ffmpeg"):
        exe_path = shutil.which(exe)
        if exe_path:
            return os.path.dirname(exe_path)

    candidates = []
    if localappdata := os.environ.get("LOCALAPPDATA"):
        candidates.extend(glob.glob(os.path.join(localappdata, "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg*", "*", "bin")))
    candidates.extend([
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "ffmpeg", "bin"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "ffmpeg", "bin"),
    ])

    for candidate in candidates:
        if os.path.isfile(os.path.join(candidate, "ffmpeg.exe")) and os.path.isfile(os.path.join(candidate, "ffprobe.exe")):
            return candidate

    return None


ffmpeg_location = find_ffmpeg_location()
if ffmpeg_location:
    ffmpeg_exe = os.path.join(ffmpeg_location, "ffmpeg.exe")
    if os.path.isfile(ffmpeg_exe):
        ffmpeg_location = ffmpeg_exe


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "js_runtimes": ["node"],
    }

    if ffmpeg_location:
        ydl_opts["ffmpeg_location"] = ffmpeg_location

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename


def get_video_id(url: str) -> str | None:
    """Return the YouTube video id for a URL without downloading the file."""
    ydl_opts = {"quiet": True, "js_runtimes": ["node"]}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("id")
    except Exception:
        return None




def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    input_path = str(input_path)
    # Ensure output is saved to DOWNLOAD_DIR
    filename = os.path.basename(input_path)
    output_path = os.path.join(DOWNLOAD_DIR, os.path.splitext(filename)[0] + "_converted.wav")
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 16 kHz mono
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    """Split WAV audio into chunks of specified duration (in minutes)."""
    audio = AudioSegment.from_file(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []
    filename = os.path.basename(wav_path)
    base_name = os.path.splitext(filename)[0]
    
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = os.path.join(DOWNLOAD_DIR, f"{base_name}_chunk_{i}.wav")
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    
    return chunks


if __name__ == "__main__":
    # Paste your YouTube URL here
    YOUTUBE_URL = "https://www.youtube.com/watch?v=Ty8gcCKuwNI"
    
    if YOUTUBE_URL and "youtube.com" in YOUTUBE_URL:
        # Download from YouTube
        print(f"Downloading from: {YOUTUBE_URL}")
        try:
            wav_file = download_youtube_audio(YOUTUBE_URL)
            convert_to_wav(wav_file) 
            print("Downloaded and converted to WAV:", wav_file)
        except Exception as e:
            print("Download failed:", e)
            exit(1)
    else:
        # Convert the most recent non-part file in DOWNLOAD_DIR to WAV
        files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if not f.endswith('.part')]
        if not files:
            print("No downloaded files found in", DOWNLOAD_DIR)
            exit(1)
        latest = max(files, key=os.path.getmtime)
        print("Converting:", latest)
        try:
            wav_file = convert_to_wav(latest)
            print("Created WAV:", wav_file)
        except Exception as e:
            print("Conversion failed:", e)
            exit(1)
    
    # Create chunks from the WAV file
    try:
        chunks = chunk_audio(wav_file, chunk_minutes=10)
        print(f"Created {len(chunks)} chunks:")
        for chunk in chunks:
            print(f"  - {chunk}")
    except Exception as e:
        print("Chunking failed:", e)






def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks




























