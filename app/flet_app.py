import flet as ft
import threading
import time
import datetime
import os
import sys
import subprocess
import textwrap  # for word wrapping

import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER

from file_handler import read_file
from chatbot import ask_chatgpt  # We assume you have a single ask_chatgpt(msg) approach

# GLOBALS to store doc content + conversation
conversation_history = []  # list of dicts: {"role": "user"|"assistant"|"system", "content": "..."}
doc_text = None  # store last loaded doc text

def open_pdf_file(pdf_path):
    if sys.platform.startswith("win"):
        os.startfile(pdf_path)  # Windows
    elif sys.platform.startswith("darwin"):
        subprocess.run(["open", pdf_path])  # macOS
    else:
        subprocess.run(["xdg-open", pdf_path])  # Linux

def main(page: ft.Page):
    page.title = "GPT-4o Assistant (Dark Default, Local PDF Save, Faster Typing, Word-Wrapped PDF)"
    # Dark theme by default:
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START

    chat_column = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        expand=True,
        spacing=10,
        auto_scroll=True
    )

    chat_frame = ft.Container(
        content=chat_column,
        # Initially, let's keep the background set for dark theme:
        bgcolor="#2A2A2A",  # a nice dark gray
        border_radius=12,
        padding=20,
        expand=True,
        border=ft.border.all(1, ft.Colors.GREY_600),
        animate_opacity=300
    )

    def set_theme_background():
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.bgcolor = "#F0F2F5"
            chat_frame.bgcolor = "#FFFFFF"
            chat_frame.border = ft.border.all(1, ft.Colors.GREY_300)
        else:
            page.bgcolor = "#121212"
            chat_frame.bgcolor = "#2A2A2A"
            chat_frame.border = ft.border.all(1, ft.Colors.GREY_600)

        page.update()

    def toggle_theme(e):
        # If dark, switch to light, else dark
        page.theme_mode = (
            ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        )
        update_theme_icon()
        set_theme_background()

    def update_theme_icon():
        if page.theme_mode == ft.ThemeMode.DARK:
            # If currently dark, show an icon to switch to Light:
            theme_toggle.icon = ft.Icons.LIGHT_MODE
            theme_toggle.tooltip = "Switch to Light"
        else:
            # If currently light, show an icon to switch to Dark:
            theme_toggle.icon = ft.Icons.DARK_MODE
            theme_toggle.tooltip = "Switch to Dark"
        theme_toggle.update()

    def bubble_color(is_user=False):
        # user bubble vs assistant bubble color
        # For Dark mode, let's keep them distinct:
        return "#1E88E5" if is_user else "#2E7D32"

    def avatar(is_user=False):
        return ft.CircleAvatar(
            content=ft.Text("U" if is_user else "G", size=12, weight=ft.FontWeight.BOLD),
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_500 if is_user else ft.Colors.GREY_600,
            radius=14
        )

    def make_chat_bubble(text, is_user=False):
        """
        Build a bubble container for user or assistant.
        Return row + references so we can do a chunk-based typing effect for the assistant.
        """
        time_str = datetime.datetime.now().strftime("%H:%M")

        # In Dark mode, let's keep text white, as we do:
        main_text = ft.Text(text, selectable=True, color=ft.Colors.WHITE)
        time_text = ft.Text(time_str, size=10, color=ft.Colors.GREY_400, italic=True)

        bubble = ft.Container(
            content=ft.Column([
                main_text,
                time_text
            ]),
            alignment=ft.alignment.top_right if is_user else ft.alignment.top_left,
            padding=10,
            margin=10,
            bgcolor=bubble_color(is_user),
            border_radius=12,
            width=500,
            opacity=0.0,
            offset=ft.Offset(0, 0.1),
            animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
        )
        row = ft.Row(
            controls=[avatar(is_user), bubble] if not is_user else [bubble, avatar(is_user)],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
        )
        return row, bubble, main_text, time_text

    def show_user_bubble(text):
        """
        Immediately shows the entire user text (no chunking).
        """
        row, bubble, main_text, time_text = make_chat_bubble(text, is_user=True)
        chat_column.controls.append(row)
        chat_column.update()
        time.sleep(0.05)
        bubble.opacity = 1.0
        bubble.offset = ft.Offset(0, 0)
        bubble.update()

    # Faster chunk-based typing
    CHUNK_SIZE = 3
    TYPING_DELAY = 0.01

    def show_assistant_bubble_typing(full_text):
        """
        Types out the assistant response chunk by chunk, for a faster effect.
        """
        row, bubble, main_text, time_text = make_chat_bubble("", is_user=False)
        chat_column.controls.append(row)
        chat_column.update()

        time.sleep(0.05)
        bubble.opacity = 1.0
        bubble.offset = ft.Offset(0,0)
        bubble.update()

        typed = ""
        for i in range(0, len(full_text), CHUNK_SIZE):
            chunk = full_text[i:i+CHUNK_SIZE]
            typed += chunk
            main_text.value = typed
            bubble.update()
            time.sleep(TYPING_DELAY)

        # final update for timestamp
        time_text.value = datetime.datetime.now().strftime("%H:%M")
        bubble.update()

    # For picking files (like CSV or doc)
    def pick_file(e):
        global doc_text, conversation_history
        if not e.files:
            return
        path = e.files[0].path
        file_contents = read_file(path)
        doc_text = file_contents

        show_assistant_bubble_typing(f"Document loaded: {path}\nDoc content stored in memory.")
        conversation_history.append({"role": "system", "content": f"Document context loaded:\n{doc_text}"})

    # For resetting everything
    def reset_conversation(e):
        global doc_text, conversation_history
        doc_text = None
        conversation_history = []
        show_assistant_bubble_typing("Memory cleared!")

    # For sending queries to GPT
    def send_message():
        msg = user_input.value.strip()
        if not msg:
            return
        user_input.value = ""
        user_input.update()

        # user bubble
        show_user_bubble(msg)
        conversation_history.append({"role":"user","content": msg})

        # 'typing...' text
        typing_txt = ft.Text("Assistant is typing...", italic=True, size=12, color=ft.Colors.GREY_400)
        chat_column.controls.append(typing_txt)
        chat_column.update()

        def run_gpt():
            # Flatten conversation
            flattened = ""
            for c in conversation_history:
                role = c["role"]
                content = c["content"]
                if role == "system":
                    flattened += f"[System message]: {content}\n"
                elif role == "user":
                    flattened += f"User: {content}\n"
                else:
                    flattened += f"Assistant: {content}\n"

            prompt = flattened + "Assistant:"
            response = ask_chatgpt(prompt)

            # remove typing
            chat_column.controls.remove(typing_txt)
            chat_column.update()

            conversation_history.append({"role":"assistant","content": response})

            # chunk-based typed effect
            show_assistant_bubble_typing(response)

        threading.Thread(target=run_gpt).start()

    ## PDF Export: Save in local temp folder, then OS-based open
    MAX_WIDTH_CHARS = 100  # for word-wrapping

    def create_pdf_from_conversation(convo, pdf_path):
        c = canvas.Canvas(pdf_path, pagesize=LETTER)
        width, height = LETTER

        text_obj = c.beginText(50, height - 50)
        text_obj.setFont("Helvetica", 12)

        import textwrap
        for entry in convo:
            role = entry["role"].upper()
            content = entry["content"]
            line_str = f"{role}: {content}"
            wrapped_lines = textwrap.wrap(line_str, width=MAX_WIDTH_CHARS)
            for wl in wrapped_lines:
                text_obj.textLine(wl)
            text_obj.textLine("")

        c.drawText(text_obj)
        c.showPage()
        c.save()

    def export_chat_local(e):
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)

        pdf_path = os.path.join(temp_dir, "chat_history.pdf")
        create_pdf_from_conversation(conversation_history, pdf_path)

        def on_click_open_pdf(_):
            open_pdf_file(pdf_path)

        file_link_btn = ft.ElevatedButton(
            text="Open PDF",
            on_click=on_click_open_pdf
        )
        chat_column.controls.append(file_link_btn)
        chat_column.update()

        show_assistant_bubble_typing(f"Chat exported to {pdf_path}\nClick 'Open PDF' button above.")

    # UI components
    user_input = ft.TextField(
        label="Type your message",
        multiline=False,
        expand=True,
        border_radius=8,
        filled=True,
        bgcolor="#1E1E1E",  # dark text field
        color=ft.Colors.WHITE,
        border_color=ft.Colors.GREY_600,
        on_submit=lambda e: send_message()
    )

    theme_toggle = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE,  # because we start in dark mode
        tooltip="Switch to Light",
        on_click=toggle_theme
    )

    reset_button = ft.ElevatedButton("Reset Memory", on_click=reset_conversation)
    export_button = ft.ElevatedButton("Export Chat (Local PDF)", on_click=export_chat_local)

    page.on_theme_change = lambda _: update_theme_icon()

    top_row = ft.Row(
        controls=[theme_toggle, reset_button, export_button],
        alignment=ft.MainAxisAlignment.END,
        width=700,
        height=40,
    )

    file_picker = ft.FilePicker(on_result=pick_file)
    page.overlay.append(file_picker)

    page.add(
        ft.Container(
            content=top_row,
            padding=ft.padding.only(right=10, top=10)
        ),
        ft.Container(
            content=chat_frame,
            margin=ft.margin.only(top=5),
            padding=ft.padding.symmetric(horizontal=20),
            expand=True
        ),
        ft.Row([
            user_input,
            ft.ElevatedButton("Send", on_click=lambda e: send_message()),
            ft.ElevatedButton("Load File", on_click=lambda e: file_picker.pick_files())
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        height=60,
        width=700)
    )

    # Now we set the initial background for dark theme
    update_theme_icon()
    set_theme_background()

ft.app(target=main)
