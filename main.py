from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pandas as pd
import os
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# -------------------- CONFIG --------------------
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CSV_PATH = "/app/data/file_map.csv"  # Koyeb volume path

# Load environment variables
FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")  # Google Drive folder ID
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")  # JSON content as env var

# -------------------- INIT --------------------
app = FastAPI()

def generate_csv_from_drive():
    """Fetch files from Google Drive folder and generate CSV"""
    service_account_info = json.loads(SERVICE_ACCOUNT_JSON)
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)

    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        pageSize=1000,
        fields="files(id, name)"
    ).execute()
    items = results.get("files", [])

    data = []
    for f in items:
        userid = os.path.splitext(f['name'])[0].strip().lower()  # filename without extension
        fileid = f['id']
        data.append({"userid": userid, "fileid": fileid})

    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    df.to_csv(CSV_PATH, index=False)
    print(f"CSV updated with {len(items)} files.")

def load_file_map():
    df = pd.read_csv(CSV_PATH)
    return {str(k).strip().lower(): str(v).strip() for k, v in zip(df["userid"], df["fileid"])}

@app.on_event("startup")
def startup_event():
    generate_csv_from_drive()
    global file_map
    file_map = load_file_map()

# -------------------- HOME PAGE --------------------
HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Employee Document Portal</title>
<style>
body {font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #74ebd5, #ACB6E5); display:flex; justify-content:center; align-items:center; height:100vh; margin:0;}
.card {background-color:#fff; padding:30px; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,0.2); width:90%; max-width:400px; text-align:center; transition: transform 0.3s;}
.card:hover { transform: translateY(-5px); }
.card h2 { margin-bottom: 25px; color:#333; font-size:24px; }
input[type=text] {width:100%; padding:12px; border-radius:8px; border:1px solid #ccc; margin-bottom:20px; font-size:16px; box-sizing:border-box;}
button {width:100%; padding:14px; border:none; border-radius:8px; background-color:#4CAF50; color:white; font-size:16px; cursor:pointer; transition: background 0.3s;}
button:hover { background-color:#45a049; }
@media (max-width:480px) {.card {padding:20px;} h2 {font-size:20px;} input[type=text], button {font-size:14px; padding:12px;}}
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

# -------------------- PAGE TEMPLATE --------------------
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
        body {{font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #74ebd5, #ACB6E5); display:flex; justify-content:center; align-items:center; height:100vh; margin:0;}}
        .card {{background-color:#fff; padding:30px; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,0.2); width:90%; max-width:400px; text-align:center;}}
        h2 {{color:{color}; margin-bottom:25px; font-size:24px;}}
        p {{font-size:16px;}}
        a button {{padding:14px; border:none; border-radius:8px; background-color:{color}; color:white; font-size:16px; cursor:pointer; margin-top:20px;}}
        a button:hover {{background-color:{color if success else '#d32f2f'};}}
        @media (max-width:480px) {{.card {{padding:20px;}} h2 {{font-size:20px;}} p, a button {{font-size:14px; padding:12px;}}}}
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

# -------------------- ROUTES --------------------
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
