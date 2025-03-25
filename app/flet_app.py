# Python
import flet as ft
import threading
import time
import datetime
import os
import sys
import subprocess

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER

from storage.file_handler import read_file
from services.ai_service import ask_chatgpt

conversation_history = []
doc_text = None


# ----------------------------------------
# OS-specific function to open a local PDF
# ----------------------------------------
def open_pdf_file(pdf_path):
    if sys.platform.startswith("win"):
        os.startfile(pdf_path)  # Windows
    elif sys.platform.startswith("darwin"):
        subprocess.run(["open", pdf_path])  # macOS
    else:
        subprocess.run(["xdg-open", pdf_path])  # Linux


def main(page: ft.Page):
    page.title = "GPT-4o Assistant"
    # Default to Light theme, let user toggle to Dark:
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.scroll = ft.ScrollMode.AUTO

    # ----------------------------------------
    # Chat area (scrollable)
    # ----------------------------------------
    chat_column = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    chat_frame = ft.Container(
        content=chat_column,
        bgcolor="#FFFFFF",
        border_radius=12,
        padding=20,
        border=ft.border.all(1, ft.Colors.GREY_300),
        animate_opacity=300,
        expand=True
    )

    # ----------------------------------------
    # Helper function to pick side panel gradient per theme
    # ----------------------------------------
    def get_side_panel_gradient():
        """
        Returns a different gradient for the side panel
        depending on whether the theme is light or dark.
        """
        if page.theme_mode == ft.ThemeMode.LIGHT:
            return ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#FFFFFF", "#D3D3D3"]
            )
        else:
            return ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#333333", "#111111"]
            )

    # ----------------------------------------
    # Theme handling
    # ----------------------------------------
    def set_theme_background():
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.bgcolor = "#F0F2F5"
            chat_frame.bgcolor = "#FFFFFF"
            chat_frame.border = ft.border.all(1, ft.Colors.GREY_300)
        else:
            page.bgcolor = "#121212"
            chat_frame.bgcolor = "#2A2A2A"
            chat_frame.border = ft.border.all(1, ft.Colors.GREY_600)

        # Update the side panel gradient whenever the theme changes
        side_panel_container.gradient = get_side_panel_gradient()

        page.update()

    def update_theme_icon():
        if page.theme_mode == ft.ThemeMode.DARK:
            theme_toggle.icon = ft.Icons.LIGHT_MODE
            theme_toggle.tooltip = "Switch to Light"
        else:
            theme_toggle.icon = ft.Icons.DARK_MODE
            theme_toggle.tooltip = "Switch to Dark"
        theme_toggle.update()

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        )
        update_theme_icon()
        set_theme_background()

    # ----------------------------------------
    # Chat bubble utilities
    # ----------------------------------------
    def bubble_color(is_user=False):
        # Subtler background colors for chat bubbles
        return "#1565C0" if is_user else "#2E7D32"

    def avatar(is_user=False):
        return ft.CircleAvatar(
            content=ft.Text("U" if is_user else "G", size=12, weight=ft.FontWeight.BOLD),
            color=ft.Colors.WHITE,
            bgcolor="#1976D2" if is_user else "#424242",
            radius=14
        )

    def make_chat_bubble(text, is_user=False):
        time_str = datetime.datetime.now().strftime("%H:%M")
        # Text color always white for better visibility
        text_color = ft.Colors.WHITE
        main_text = ft.Text(text, selectable=True, color=text_color)
        time_text = ft.Text(time_str, size=10, color="#CCCCCC", italic=True)

        bubble = ft.Container(
            content=ft.Column([main_text, time_text], tight=True),
            alignment=ft.alignment.top_right if is_user else ft.alignment.top_left,
            padding=10,
            margin=5,
            bgcolor=bubble_color(is_user),
            border_radius=10,
            width=500,
            opacity=0.0,
            offset=ft.Offset(0, 0.04),
            animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
        )

        row = ft.Row(
            controls=[avatar(is_user), bubble] if not is_user else [bubble, avatar(is_user)],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
        )
        return row, bubble, main_text, time_text

    def show_user_bubble(text):
        row, bubble, main_text, time_text = make_chat_bubble(text, is_user=True)
        chat_column.controls.append(row)
        chat_column.update()
        time.sleep(0.05)
        bubble.opacity = 1.0
        bubble.offset = ft.Offset(0, 0)
        bubble.update()

    CHUNK_SIZE = 3
    TYPING_DELAY = 0.01

    def show_assistant_bubble_typing(full_text):
        row, bubble, main_text, time_text = make_chat_bubble("", is_user=False)
        chat_column.controls.append(row)
        chat_column.update()

        time.sleep(0.05)
        bubble.opacity = 1.0
        bubble.offset = ft.Offset(0, 0)
        bubble.update()

        typed = ""
        for i in range(0, len(full_text), CHUNK_SIZE):
            typed += full_text[i: i + CHUNK_SIZE]
            main_text.value = typed
            bubble.update()
            time.sleep(TYPING_DELAY)
        time_text.value = datetime.datetime.now().strftime("%H:%M")
        bubble.update()

    # ----------------------------------------
    # File picking + doc loading
    # ----------------------------------------
    def pick_file(e):
        global doc_text, conversation_history
        if not e.files:
            return
        path = e.files[0].path
        file_contents = read_file(path)
        doc_text = file_contents

        loaded_msg = (
            f"Document loaded: {path}\n"
            f"Doc content stored in memory.\n"
            f"Data agent is now active."
        )
        show_assistant_bubble_typing(loaded_msg)
        conversation_history.append({"role": "system", "content": f"Document context:\n{doc_text}"})

    file_picker = ft.FilePicker(on_result=pick_file)
    page.overlay.append(file_picker)

    # ----------------------------------------
    # Conversation controls
    # ----------------------------------------
    def reset_conversation(e):
        global doc_text, conversation_history
        doc_text = None
        conversation_history = []
        show_assistant_bubble_typing("Memory cleared!")

    def send_message():
        msg = user_input.value.strip()
        if not msg:
            return
        user_input.value = ""
        user_input.update()

        show_user_bubble(msg)
        conversation_history.append({"role": "user", "content": msg})

        typing_txt = ft.Text("Assistant is typing...", italic=True, size=12, color="#666666")
        chat_column.controls.append(typing_txt)
        chat_column.update()

        def run_gpt():
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

            chat_column.controls.remove(typing_txt)
            chat_column.update()
            conversation_history.append({"role": "assistant", "content": response})
            show_assistant_bubble_typing(response)

        threading.Thread(target=run_gpt).start()

    # ----------------------------------------
    # PDF Export
    # ----------------------------------------
    MAX_WIDTH_CHARS = 100

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

        file_link_btn = ft.ElevatedButton("Open PDF", on_click=on_click_open_pdf)
        chat_column.controls.append(file_link_btn)
        chat_column.update()

        show_assistant_bubble_typing(
            f"Chat exported to {pdf_path}\nClick 'Open PDF' button above."
        )

    # ----------------------------------------
    # UI Components
    # ----------------------------------------
    user_input = ft.TextField(
        label="Type your message...",
        multiline=False,
        expand=True,
        border_radius=8,
        filled=True,
        bgcolor="#FAFAFA",
        color="#111111",
        border_color="#CCCCCC",
        on_submit=lambda e: send_message()
    )

    send_button = ft.ElevatedButton("Send", on_click=lambda e: send_message())

    # Controls: theme toggle, reset, export, load
    theme_toggle = ft.IconButton(icon=ft.Icons.DARK_MODE, tooltip="Switch to Dark", on_click=toggle_theme)
    reset_button = ft.ElevatedButton("Reset Memory", on_click=reset_conversation)
    export_button = ft.ElevatedButton("Export (PDF)", on_click=export_chat_local)
    load_button = ft.ElevatedButton("Load File", on_click=lambda e: file_picker.pick_files())

    side_panel = ft.Column(
        [
            ft.Text("Controls", weight=ft.FontWeight.BOLD),
            theme_toggle,
            reset_button,
            export_button,
            load_button
        ],
        spacing=20
    )

    # We wrap side_panel in a container that uses our gradient
    side_panel_container = ft.Container(
        content=side_panel,
        width=180,
        padding=10,
        gradient=get_side_panel_gradient(),  # initial gradient
    )

    # Bottom row: user input
    bottom_row = ft.Row(
        controls=[user_input, send_button],
        spacing=10
    )

    # Main chat area: chat + bottom row
    main_chat_area = ft.Column(
        [
            chat_frame,
            ft.Container(
                content=bottom_row,
                margin=ft.margin.symmetric(vertical=10),
            ),
        ],
        expand=True
    )

    # Overall layout: side panel + chat area
    layout_row = ft.Row(
        [
            side_panel_container,
            main_chat_area
        ],
        expand=True
    )

    page.add(layout_row)
    page.on_theme_change = lambda _: update_theme_icon()
    update_theme_icon()
    set_theme_background()


ft.app(target=main)
