import os

def load_file(file_path):
    if not os.path.exists(file_path):
        return f"[Missing file: {file_path}]"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_character(name, char_dir):
    return load_file(os.path.join(char_dir, f"{name}.md"))

def load_location(name, loc_dir):
    return load_file(os.path.join(loc_dir, f"{name}.md"))

def load_scenario(name, scen_dir):
    return load_file(os.path.join(scen_dir, f"{name}.md"))
