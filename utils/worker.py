import threading
import time
from typing import Callable

from utils.cache import get_cached_result, set_cached_result
from utils.audio_processor import process_input, get_video_id
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain


def _run_pipeline(source: str, language: str, video_key: str, progress_cb: Callable[[str], None]) -> dict:
    progress_cb("Processing audio/video input…")
    chunks = process_input(source)

    progress_cb("Transcribing…")
    transcript = transcribe_all(chunks, language)

    progress_cb("Generating title…")
    title = generate_title(transcript)

    progress_cb("Summarising…")
    summary = summarize(transcript)

    progress_cb("Extracting action items…")
    action_items = extract_action_items(transcript)

    progress_cb("Extracting key decisions…")
    key_decisions = extract_key_decisions(transcript)

    progress_cb("Extracting open questions…")
    open_questions = extract_questions(transcript)

    progress_cb("Building RAG chain…")
    rag_chain = build_rag_chain(transcript)

    result = {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": key_decisions,
        "open_questions": open_questions,
        "rag_chain": rag_chain,
    }

    # Cache final result (omit rag_chain if not JSON serializable)
    cacheable = {k: v for k, v in result.items() if k != "rag_chain"}
    set_cached_result(video_key, cacheable)

    progress_cb("Complete")
    return result


def process_video_async(source: str, language: str, progress_cb: Callable[[str], None], done_cb: Callable[[dict], None]):
    """Start pipeline in a background thread and call done_cb(result) when finished."""
    def target():
        video_key = get_video_id(source) or str(time.time())
        cached = get_cached_result(video_key)
        if cached:
            progress_cb("Loaded from cache")
            cached["rag_chain"] = None
            done_cb(cached)
            return

        try:
            result = _run_pipeline(source, language, video_key, progress_cb)
            done_cb(result)
        except Exception as e:
            progress_cb(f"Error: {e}")
            done_cb({"error": str(e)})

    thread = threading.Thread(target=target, daemon=True)
    try:
        from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
        if get_script_run_ctx():
            add_script_run_ctx(thread)
    except ImportError:
        pass
    thread.start()
    return thread
