# generate_response.py
import subprocess
from config import CHAR_DIR, LOC_DIR, SCEN_DIR, MODEL, GPU_ENABLED, MAX_TOKENS
from scenarios import load_character, load_location, load_scenario
from world_manager import load_world_state, save_world_state
from entity_manager import detect_and_store_entity, load_entity

MAX_HISTORY_LINES = 10  # keep recent history to avoid prompt overload

def truncate_history(history):
    """Keep only the last N entries to avoid overflowing the prompt."""
    return history[-MAX_HISTORY_LINES:]

def build_context(active_characters=None, active_locations=None, active_scenario=None):
    """Build context from vault and world state."""
    context_parts = []

    # Characters
    if active_characters:
        for char in active_characters:
            try:
                context_parts.append(load_entity(char))
            except Exception as e:
                context_parts.append(f"[Missing character {char}: {e}]")

    # Locations
    if active_locations:
        for loc in active_locations:
            try:
                context_parts.append(load_location(loc, LOC_DIR))
            except Exception as e:
                context_parts.append(f"[Missing location {loc}: {e}]")

    # Scenario
    if active_scenario:
        try:
            context_parts.append(load_scenario(active_scenario, SCEN_DIR))
        except Exception as e:
            context_parts.append(f"[Missing scenario {active_scenario}: {e}]")

    # World state
    world_state = load_world_state()
    context_parts.append("World State:\n" + str(world_state))

    return "\n\n".join(context_parts)

def generate_response(input_text, history=None, active_characters=None,
                      active_locations=None, active_scenario=None,
                      debug=False):
    """Generate AI narrative response."""
    if history is None:
        history = []

    # Detect and store new entities if introduced
    detect_and_store_entity(input_text)

    # Truncate history
    truncated_history = truncate_history(history)

    # Build full context
    context = build_context(active_characters, active_locations, active_scenario)

    # Merge truncated history
    conversation = ""
    for entry in truncated_history:
        # Ollama GGUF expects free text without role labels
        conversation += f"{entry['content']}\n"
    conversation += f"{input_text}"

    # Full input to model
    full_input = f"""
You are a narrative AI assistant for HistorIA.
You control all characters except 'Master', who is always controlled by the user.
Narrate other characters’ actions, gestures, dialogue, and reactions immersively.
Never overwrite or roleplay Master.
Use world state and vault knowledge (characters, locations, scenarios) to continue the story naturally.
Maintain continuity and logical progression.
Update world state when characters enter, exit, or interact.
Respond in full immersive narrative.
Night mode: immersive, suspenseful atmosphere.

World State:
{str(load_world_state())}

Story so far:
{conversation}

User Input:
{input_text}
"""

    if debug:
        print("=== FULL INPUT SENT TO MODEL ===")
        print(full_input)

    # --- Ollama GGUF command ---
    cmd = ["ollama", "run", MODEL]

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        response, err = process.communicate(input=full_input, timeout=60)
        response = response.strip()
        if not response:
            response = "[No response from model]"

        if debug:
            print("=== MODEL STDERR ===")
            print(err)
            print("=== RAW RESPONSE ===")
            print(response)

    except subprocess.TimeoutExpired:
        response = "[Error: AI model timed out]"
    except Exception as e:
        response = f"[Error generating response: {e}]"

    # --- Update history ---
    history.append({"role": "user", "content": input_text})

    # For testing/debug purposes only
    if debug:
        world_state_snapshot = str(load_world_state())
        history.append({"role": "system", "content": f"[World State Snapshot: {world_state_snapshot}]"})
    
    history.append({"role": "assistant", "content": response})

    # Return narrative only for production
    return response, history
