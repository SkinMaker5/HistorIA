import os
import re
from src.config import CHAR_DIR

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def save_or_update_entity(category, name, content, overwrite=True):
    os.makedirs(CHAR_DIR, exist_ok=True)
    path = os.path.join(CHAR_DIR, sanitize_filename(name) + ".md")
    if os.path.exists(path) and not overwrite:
        return f"{category.capitalize()} '{name}' already exists."
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"{category.capitalize()} '{name}' created/updated successfully."

def load_entity(name):
    filename = sanitize_filename(name) + ".md"
    path = os.path.join(CHAR_DIR, filename)
    if not os.path.exists(path):
        content = f"""# {name}

**Description:** 

**Personality Traits:**

**Abilities:** 

**Known Relationships:**

**Attire/Outfit:**
- Default Outfit:
- Temporary Outfit:

**Current Status:**
- Current Mood: Neutral
- Location: Unknown

**Special Notes:**
"""
        save_or_update_entity("character", name, content)
        return content
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def update_status(name, mood=None, location=None):
    content = load_entity(name)
    if mood:
        content = re.sub(r'(- Current Mood: ).*', f'\\1{mood}', content)
    if location:
        content = re.sub(r'(- Location: ).*', f'\\1{location}', content)
    save_or_update_entity("character", name, content)

def update_outfit(name, default=None, temporary=None):
    content = load_entity(name)
    if default:
        content = re.sub(r'(- Default Outfit:).*', f'\\1 {default}', content)
    if temporary:
        content = re.sub(r'(- Temporary Outfit:).*', f'\\1 {temporary}', content)
    save_or_update_entity("character", name, content)


def update_relationship(name, other, relation):
    content = load_entity(name)
    if "**Known Relationships:**" not in content:
        content += "\n**Known Relationships:**\n"
    pattern = re.compile(r'(\*\*Known Relationships:\*\*\n(?:- .*\n)*)', re.MULTILINE)
    match = pattern.search(content)
    if match:
        rel_block = match.group(1)
        if f"- {other}:" in rel_block:
            rel_block = re.sub(rf'(- {other}:).*', f'\\1 {relation}', rel_block)
        else:
            rel_block += f"- {other}: {relation}\n"
        content = content[:match.start(1)] + rel_block + content[match.end(1):]
    save_or_update_entity("character", name, content)

def detect_and_store_entity(input_text):
    match = re.match(r'([A-Z][a-zA-Z0-9]+)\s+(.+)', input_text)
    if match:
        name = match.group(1)
        desc = match.group(2)
        content = load_entity(name)
        if "**Description:**" in content:
            content = re.sub(r'(\*\*Description:\*\*).*', f'\\1 {desc}', content)
        else:
            content += f"\n**Description:** {desc}\n"
        save_or_update_entity("character", name, content)
        return f"[Updated character: *{name}]"
    return None


