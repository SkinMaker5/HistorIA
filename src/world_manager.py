import json
import os
from src.config import WORLD_STATE_FILE

def load_world_state() -> dict:
    if os.path.exists(WORLD_STATE_FILE):
        with open(WORLD_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # default empty state
    return {
        "characters_in_room": [],
        "locations": [],
        "last_actions": [],
        "first_visit": True,
        "last_scene_summary": ""
    }

def save_world_state(state: dict):
    with open(WORLD_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def is_first_visit():
    state = load_world_state()
    return state.get("first_visit", True)

def set_first_visit_done():
    state = load_world_state()
    state["first_visit"] = False
    save_world_state(state)

def update_last_scene_summary(summary: str):
    state = load_world_state()
    state["last_scene_summary"] = summary
    save_world_state(state)

def get_refresh_greeting():
    state = load_world_state()
    last_scene = state.get("last_scene_summary", "")
    if last_scene:
        return "Welcome back! Here's what’s happening:\n" + last_scene
    return ""

