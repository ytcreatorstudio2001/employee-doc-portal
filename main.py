from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

import pandas as pd

app = FastAPI()

# Environment variables
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")

# Function to generate in-memory file map from Google Drive
def generate_file_map():
    creds = service_account.Credentials.from_service_account_info(
        json.loads(SERVICE_ACCOUNT_JSON),
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()
    files = results.get('files', [])
    return {f['name'].split('.')[0].strip().lower(): f['id'] for f in files}

# Generate file map on startup
file_map = generate_file_map()

# Home page
HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Employee Document Portal</title>
<style>
body { font-family: Arial, sans-serif; background: #f0f2f5; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }
.card { background:#fff; padding:30px; border-radius:12px; box-shadow:0 5px 15px rgba(0,0,0,0.2); width:90%; max-width:400px; text-align:center; }
h2 { margin-bottom:20px; color:#333; }
input[type=text] { width:100%; padding:12px; margin-bottom:20px; border-radius:8px; border:1px solid #ccc; font-size:16px; }
button { width:100%; padding:14px; border:none; border-radius:8px; background-color:#4CAF50; color:white; font-size:16px; cursor:pointer; }
button:hover { background-color:#45a049; }
a button { width:100%; padding:14px; margin-top:15px; }
</style>
</head>
<body>
<div class="card">
<h2>Employee Document Download</h2>
<form action="/download" method="post">
<input type="text" name="userid" placeholder="Enter your User ID" required />
<button type="submit">Download</button>
</form>
</div>
</body>
</html>
"""

# Generic page template
def page_template(title, message, button_text=None, button_link=None, success=True):
    color = "#4CAF50" if success else "#f44336"
    button_html = f'<a href="{button_link}"><button>{button_text}</button></a>' if button_text and button_link else ""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
    body {{ font-family: Arial, sans-serif; background:#f0f2f5; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }}
    .card {{ background:#fff; padding:30px; border-radius:12px; box-shadow:0 5px 15px rgba(0,0,0,0.2); width:90%; max-width:400px; text-align:center; }}
    h2 {{ color:{color}; margin-bottom:20px; }}
    p {{ font-size:16px; }}
    a button {{ padding:14px; border:none; border-radius:8px; background-color:{color}; color:white; font-size:16px; cursor:pointer; margin-top:15px; }}
    a button:hover {{ background-color:{color if success else '#d32f2f'}; }}
    </style>
    </head>
    <body>
    <div class="card">
    <h2>{title}</h2>
    <p>{message}</p>
    {button_html}
    </div>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def home():
    return HOME_PAGE

@app.post("/download")
async def download(userid: str = Form(...)):
    userid = userid.strip().lower()
    fileid = file_map.get(userid)
    if fileid:
        url = f"https://drive.google.com/uc?export=download&id={fileid}"
        return HTMLResponse(page_template(
            title="✅ File Ready for Download",
            message=f'<a href="{url}" target="_blank" style="color:#2196F3;">Click here to download your document</a>',
            button_text="Go Back",
            button_link="/",
            success=True
        ))
    else:
        return HTMLResponse(page_template(
            title="❌ Invalid User ID",
            message="The User ID you entered was not found. Please check and try again.",
            button_text="Go Back",
            button_link="/",
            success=False
        ))
