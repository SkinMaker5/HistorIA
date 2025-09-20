import os
from src.entity_manager import save_or_update_entity, load_entity

active_characters = []

def get_active_characters():
    return active_characters

def add_character(name):
    if name not in active_characters:
        active_characters.append(name)
        return f"Character '{name}' added to the session."
    return f"Character '{name}' is already active."

def remove_character(name):
    if name in active_characters:
        active_characters.remove(name)
        return f"Character '{name}' removed from the session."
    return f"Character '{name}' is not active."

def list_characters():
    return active_characters

def add_note(name, content, category="characters"):
    category_map = {"characters": "characters"}
    if category not in category_map:
        return f"Unknown category '{category}'."
    result = save_or_update_entity(category, name, content)
    if category == "characters":
        add_character(name)
    return result

