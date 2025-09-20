# Gradio_test.py
import gradio as gr
from main import chat
from entity_manager import detect_and_store_entity, save_entity, load_entity


# Initialize chat history
history = []

def test_chat(user_input):
    global history
    history, _ = chat(user_input, history)
    # Return only the last AI response
    return history[-1]["content"]

with gr.Blocks() as demo:
    gr.Markdown("## HistorIA Test Chat")
    
    chatbot = gr.Chatbot(type="messages", elem_id="chatbox")
    msg = gr.Textbox(placeholder="Type here...", elem_id="user_input")
    clear = gr.Button("Clear Chat")
    
    # When user submits a message
    def submit_msg(user_msg, chat_history):
        response = test_chat(user_msg)
        return [(None, response)], chat_history, ""  # clear input
    
    msg.submit(submit_msg, [msg, chatbot], [chatbot, chatbot, msg])
    clear.click(lambda: ([], [], ""), None, [chatbot, chatbot, msg])

demo.launch()
