import subprocess
from src.config import CHAR_DIR, LOC_DIR, SCEN_DIR, MODEL, GPU_ENABLED, MAX_TOKENS
from src.scenarios import load_character, load_location, load_scenario
from src.world_manager import load_world_state
import re
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer, util
import json


# --- Vault & cache paths ---
VAULT_PATH = Path(__file__).parent / "HistorIA_Vault"
CACHE_FILE = Path(__file__).parent / "vault_summaries.json"

# --- Load Obsidian vault notes ---
notes = []
for file in VAULT_PATH.rglob("*.md"):
    if file.suffix == ".md":
        with open(file, "r", encoding="utf-8") as f:
            notes.append(f.read())

# --- Chunk notes ---
def chunk_text(text, max_words=800):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i:i+max_words])

chunks = list(chunk_text("\n\n".join(notes)))

# --- Summarize a chunk (via AI) ---
def summarize_chunk(chunk):
    if len(chunk.split()) < 200:  # skip short chunks
        return chunk
    prompt = f"Summarize the following text briefly, keeping all important details:\n\n{chunk}\n\nSummary:"
    cmd = ["ollama", "run", MODEL]
    if GPU_ENABLED:
        cmd.append("--gpu")
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        summary, _ = process.communicate(input=prompt, timeout=60)
        return summary.strip() if summary.strip() else chunk
    except Exception:
        return chunk

# --- Load or compute cached summaries ---
if CACHE_FILE.exists():
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        summarized_chunks = json.load(f)
else:
    summarized_chunks = [summarize_chunk(c) for c in chunks]
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(summarized_chunks, f, indent=2, ensure_ascii=False)

# --- Compute embeddings for summarized chunks ---
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chunk_embeddings = embedding_model.encode(summarized_chunks, convert_to_tensor=True)

# --- Semantic chunk selection ---
def select_relevant_chunks(user_input, chunks, embeddings, top_k=3):
    user_embedding = embedding_model.encode(user_input, convert_to_tensor=True)
    cosine_scores = util.cos_sim(user_embedding, embeddings)[0]
    
    # Make sure top_k does not exceed number of chunks
    top_k = min(top_k, len(chunks))
    
    top_results = np.argpartition(-cosine_scores, range(top_k))[:top_k]
    top_results = sorted(top_results, key=lambda i: -cosine_scores[i])
    return [chunks[i] for i in top_results]

def reload_vault_summaries():
    """Reload and recache vault summaries."""
    global chunks, summarized_chunks, chunk_embeddings
    # Reload notes
    notes.clear()
    for file in VAULT_PATH.rglob("*.md"):
        if file.suffix == ".md":
            with open(file, "r", encoding="utf-8") as f:
                notes.append(f.read())
    # Chunk & summarize
    chunks = list(chunk_text("\n\n".join(notes)))
    summarized_chunks = [summarize_chunk(c) for c in chunks]
    # Save cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(summarized_chunks, f, indent=2, ensure_ascii=False)
    # Recompute embeddings
    chunk_embeddings = embedding_model.encode(summarized_chunks, convert_to_tensor=True)
    return "Vault summaries reloaded successfully."

def generate_response(input_text, history=None, active_characters=None,
                      active_locations=None, active_scenario=None,
                      narrative_mode=False):
    if history is None:
        history = []

    context_parts = []

    # --- Load active characters ---
    if active_characters:
        for char in active_characters:
            try:
                context_parts.append(load_character(char, CHAR_DIR))
            except Exception as e:
                context_parts.append(f"[Missing character {char}: {e}]")

    # --- Load active locations ---
    if active_locations:
        for loc in active_locations:
            try:
                context_parts.append(load_location(loc, LOC_DIR))
            except Exception as e:
                context_parts.append(f"[Missing location {loc}: {e}]")

    # --- Load active scenario ---
    if active_scenario:
        try:
            context_parts.append(load_scenario(active_scenario, SCEN_DIR))
        except Exception as e:
            context_parts.append(f"[Missing scenario {active_scenario}: {e}]")

    # --- Load world memory ---
    world_state = load_world_state()
    context_parts.append("World State:\n" + str(world_state))

    # --- Build full context ---
    context = "\n\n".join(context_parts)

    # --- Build conversation/story input ---
    if narrative_mode:
        # Narrative mode: convert previous assistant messages to story
        story_so_far = "\n".join([entry['content'] for entry in history if entry['role'] == 'assistant'])
        full_input = f"Context:\n{context}\n\nStory so far:\n{story_so_far}\n\nNew Action:\n{input_text}\n\nInstruction: Continue the story as an immersive narrative. Describe characters' actions and emotions. Do not write dialogue in a chat format. Do not impersonate any character."
    else:
        # Normal chat mode
        conversation = ""
        for entry in history:
            conversation += f"{entry['role']}: {entry['content']}\n"
        conversation += f"User: {input_text}"
        full_input = f"Context:\n{context}\n\nConversation:\n{conversation}"

    # --- Run Ollama ---
    cmd = ["ollama", "run", MODEL]
    if GPU_ENABLED:
        cmd.append("--gpu")

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        response, _ = process.communicate(input=full_input, timeout=60)
        response = response.strip()
        if not response:
            response = "[No response from model]"

    except subprocess.TimeoutExpired:
        response = "[Error: AI model timed out]"
    except Exception as e:
        response = f"[Error generating response: {e}]"

    # --- Clean AI output ---
    response_lines = response.splitlines()
    cleaned_lines = [line.lstrip("+[]") for line in response_lines]
    response = "\n".join(cleaned_lines).strip()

    # --- Update history ---
    history.append({"role": "user", "content": input_text})
    history.append({"role": "assistant", "content": response})

    return response, history
