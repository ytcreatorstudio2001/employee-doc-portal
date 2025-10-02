# Employee Document Portal

A FastAPI-based portal where employees can download their documents using only their User ID.

## 🚀 Setup

### 1. Generate `file_map.csv`
- Copy `scripts/export_file_map.gs` into [Google Apps Script](https://script.google.com/).
- Replace `folderId` with your Drive folder ID.
- Run `exportFileMap` → it creates `file_map.csv` in Drive.
- Download `file_map.csv` and place it in the project root.

### 2. Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
