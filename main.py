# main.py
import gradio as gr
import os
import json
from generate_response import generate_response
from entity_manager import detect_and_store_entity, save_or_update_entity, load_entity
from dynamic_entities import get_active_characters, add_character, remove_character
from config import WORLD_STATE_FILE

# --- Chat history ---
history = []

# --- First-time greeting ---
FIRST_GREETING = """You stir awake as the soft morning light spills through the tall, ornate windows of the manor. The air carries the faint scent of fresh bread and lavender, teasing your senses, and for a moment, you savor the quiet. Then a gentle tap on your shoulder reminds you that the day has already begun.
Good morning, Sophia says, her blonde curls catching the early light as she opens the curtains with a gesture.
She steps back, gesturing lightly as if the room itself responds. We have a visitor arriving today, so the morning is a little busier. Ri can prepare a breakfast that will invigorate you for the day. Clarissa and Yuna can assist with dressing - outfits, accessories, and charms all perfectly arranged. Lily can draw a bath to refresh you, or you can supervise while I and Amara handle preparations for the guest - and Isabelle can ensure your privacy or subtly shield the household if needed.
Her eyes meet yours, calm but expectant. Which shall we begin with? Or anything else you require?
Outside your bedchamber, the day hums with life, a delicate balance of ordinary chores and extraordinary magic, and with these seven maids orchestrating it all, even the mundane feels enchanted."""

# --- Load last world state if exists ---
if os.path.exists(WORLD_STATE_FILE):
    with open(WORLD_STATE_FILE, "r", encoding="utf-8") as f:
        last_state = json.load(f)
else:
    last_state = None

# If no world state yet, show first greeting
if last_state is None or not last_state.get("greeted"):
    history.append({"role": "assistant", "content": FIRST_GREETING})
    # Mark greeted in world state
    last_state = last_state or {}
    last_state["greeted"] = True
    with open(WORLD_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(last_state, f, indent=2, ensure_ascii=False)


def chat(input_text, history):
    input_text = input_text.strip()

    # --- Special commands ---
    if input_text.lower().startswith("/addnote "):
        try:
            parts = input_text[9:].split(":", 1)
            name = parts[0].strip()
            text = parts[1].strip()
            content = load_entity(name)
            # Update description if needed
            if "**Description:**" in content:
                content = content.replace("**Description:**", f"**Description:** {text}")
            else:
                content += f"\n**Description:** {text}\n"
            save_or_update_entity(name, content)
            return history + [{"role": "system", "content": f"Character '{name}' updated successfully."}], history + [{"role": "system", "content": f"Character '{name}' updated successfully."}]
        except Exception as e:
            return history + [{"role": "system", "content": f"[Error adding note: {e}]"}], history + [{"role": "system", "content": f"[Error adding note: {e}]"}]

    if input_text.lower() == "/list":
        entities = get_active_characters()
        return history + [{"role": "system", "content": "Active characters: " + ", ".join(entities)}], history + [{"role": "system", "content": "Active characters: " + ", ".join(entities)}]

    # Auto-detect new entities from input
    detect_and_store_entity(input_text)

    # Add/remove characters dynamically if narrative says they enter/exit
    active_chars = get_active_characters()
    for name in active_chars.copy():
        if f"{name} leaves" in input_text.lower() or f"{name} exited" in input_text.lower():
            remove_character(name)

    # Generate immersive narrative response
    response, updated_history = generate_response(
        input_text=input_text,
        history=history,
        active_characters=get_active_characters()
    )

    return updated_history, updated_history


# --- Gradio interface ---
# main.py snippet
with gr.Blocks() as demo:
    gr.Markdown("## HistorIA Interactive Story")
    chatbot = gr.Chatbot(type="messages", elem_id="chatbox")
    msg = gr.Textbox(placeholder="Type here...", elem_id="user_input")
    clear = gr.Button("Clear Chat")

    def submit_msg(user_msg, history):
        new_history, updated_history = chat(user_msg, history)
        return updated_history, updated_history, ""  # clear input

    msg.submit(submit_msg, [msg, chatbot], [chatbot, chatbot, msg])
    clear.click(lambda: ([], [], ""), None, [chatbot, chatbot, msg])

demo.launch()

