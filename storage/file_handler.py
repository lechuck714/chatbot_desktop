# chatbot_desktop/storage/file_handler.py

import os
import csv
import pandas as pd
import pdfplumber
from docx import Document


def read_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        return read_pdf_plumber(file_path)
    elif ext == '.docx':
        return read_docx(file_path)
    elif ext in ['.csv', '.xlsx']:
        return read_spreadsheet_preview(file_path, ext)
    else:
        return "Unsupported file type."


def read_pdf_plumber(file_path):
    text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
    return "\n".join(text)


def read_docx(file_path):
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def read_spreadsheet_preview(file_path, ext):
    try:
        df = pd.read_csv(file_path) if ext == '.csv' else pd.read_excel(file_path)
        preview = df.head(5).to_string(index=False)
        desc = df.describe(include='all').to_string()
        return f"Preview:\n{preview}\n\nStats:\n{desc}"
    except Exception as e:
        return f"Could not read spreadsheet: {e}"
