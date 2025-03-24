import tkinter as tk
import os
from tkinter import scrolledtext
from chatbot import ask_chatgpt
from tkinter import filedialog
from file_handler import read_file

def pick_file():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    content = read_file(file_path)

    # You can modify this system prompt for more specific analysis
    prompt = f"Please analyze and summarize the following file:\n\n{content[:6000]}"  # Truncate to fit token limits
    response = ask_chatgpt(prompt)

    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"[File Analysis of: {os.path.basename(file_path)}]\n{response}\n\n")
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END)

def send_message(event=None):
    user_input = entry.get()
    if not user_input.strip():
        return

    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"You: {user_input}\n")
    chat_log.config(state=tk.DISABLED)
    entry.delete(0, tk.END)

    root.after(100, lambda: get_response(user_input))

def get_response(user_input):
    response = ask_chatgpt(user_input)

    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"Assistant: {response}\n\n")
    chat_log.yview(tk.END)
    chat_log.config(state=tk.DISABLED)

# Initialize window
root = tk.Tk()
root.title("GPT-4o Desktop Assistant")
root.geometry("800x600")
root.minsize(700, 500)


# Chat display (scrollable)
chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Segoe UI", 11))
chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_log.config(state=tk.DISABLED)

# Bottom input container
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)


entry = tk.Entry(bottom_frame, font=("Segoe UI", 11))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
entry.bind("<Return>", send_message)

send_button = tk.Button(bottom_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT)

load_button = tk.Button(bottom_frame, text="Load File", command=pick_file)
load_button.pack(side=tk.LEFT, padx=(0, 10))


entry.focus()
root.mainloop()
