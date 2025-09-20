import os

# Folders and files to ignore
IGNORE = {"ai_env", "__pycache__", ".git", ".idea", ".vscode", ".gradio", "TOOLS",".obsidian","backups"}

def print_tree_md(startpath, prefix=""):
    """Print folder structure in ASCII/Markdown-friendly format, ignoring certain folders."""
    try:
        files = sorted(f for f in os.listdir(startpath) if f not in IGNORE)
    except PermissionError:
        return  # Skip folders we can't access
    for index, file in enumerate(files):
        path = os.path.join(startpath, file)
        connector = "├─ " if index < len(files) - 1 else "└─ "
        print(prefix + connector + file)
        if os.path.isdir(path):
            extension = "│  " if index < len(files) - 1 else "   "
            print_tree_md(path, prefix + extension)

if __name__ == "__main__":
    # Replace with the path to your project
    project_path = r"C:\Users\elias\Documents\HistorIA"
    print_tree_md(project_path)

