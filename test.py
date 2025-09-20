# continuous_test.py
from generate_response import generate_response
from dynamic_entities import add_character, get_active_characters, remove_character

# Initialize chat history
history = []

# First-time greeting
FIRST_GREETING = "You stir awake as the soft morning light spills through the tall, ornate windows..."
history.append({"role": "assistant", "content": FIRST_GREETING})
print("=== FIRST GREETING ===\n", FIRST_GREETING, "\n=====================\n")

# Add characters
add_character("Thalya")
add_character("Sophia")

# Example adventure steps
adventure_steps = [
    "*Master sits at his desk, reviewing papers intensely.*",
    "*Thalya enters Master's office holding a cup of coffee.*",
    '"Darling, you should rest; overworking is not good."',
    '"I can give you a massage if you allow me," said Thalya in a flirty tone.',
    '"I cannot do that my love," said Master, unable to remove his eyes from the papers.',
    "*Sophia, the headmaid, enters the room carrying a silver tray.*",
    "*Thalya notices Sophia for the first time and smiles politely.*",
    "*Thalya leaves the room to attend the garden.*"
]

for step in adventure_steps:
    response, history = generate_response(
        input_text=step,
        history=history,
        active_characters=get_active_characters()
    )
    print(f"User: {step}")
    print(f"AI: {response}\n")

