from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
import asyncio
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = FastAPI()

# --- Environment Variables ---
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_JSON")  # Paste JSON content here or use Koyeb env
FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")           # e.g., "1VuY6jM-a8UJi4hHs1sJ6z30O2dYjksl1"

# --- Google Drive API Setup ---
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
credentials = service_account.Credentials.from_service_account_info(
    eval(SERVICE_ACCOUNT_FILE), scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

# --- Function to generate file map ---
def generate_file_map():
    """Fetch all files from folder and create {userid: fileid} mapping"""
    file_map = {}
    page_token = None
    while True:
        results = drive_service.files().list(
            q=f"'{FOLDER_ID}' in parents and trashed=false",
            spaces='drive',
            fields="nextPageToken, files(id, name)",
            pageToken=page_token
        ).execute()
        items = results.get('files', [])
        for item in items:
            userid = os.path.splitext(item['name'])[0].strip().lower()
            file_map[userid] = item['id']
        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break
    print(f"Loaded {len(file_map)} files from Drive.")
    return file_map

# --- Initial file map ---
file_map = generate_file_map()

# --- Background task to auto-refresh ---
REFRESH_INTERVAL = 5 * 60  # 5 minutes

async def refresh_file_map_periodically():
    global file_map
    while True:
        try:
            print("Refreshing file map from Google Drive...")
            file_map = generate_file_map()
        except Exception as e:
            print(f"Error refreshing file map: {e}")
        await asyncio.sleep(REFRESH_INTERVAL)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(refresh_file_map_periodically())

# --- HTML Pages ---
HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Employee Document Portal</title>
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #74ebd5, #ACB6E5); display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .card { background-color: #fff; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 90%; max-width: 400px; text-align: center; transition: transform 0.3s; }
    .card:hover { transform: translateY(-5px); }
    .card h2 { margin-bottom: 25px; color: #333; font-size: 24px; }
    input[type=text] { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ccc; margin-bottom: 20px; font-size: 16px; box-sizing: border-box; }
    button { width: 100%; padding: 14px; border: none; border-radius: 8px; background-color: #4CAF50; color: white; font-size: 16px; cursor: pointer; transition: background 0.3s; }
    button:hover { background-color: #45a049; }
    a button { width: 100%; padding: 14px; font-size: 16px; }
    @media (max-width: 480px) { .card { padding: 20px; } h2 { font-size: 20px; } input[type=text], button, a button { font-size: 14px; padding: 12px; } }
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
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #74ebd5, #ACB6E5); display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }}
        .card {{ background-color:#fff; padding:30px; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,0.2); width:90%; max-width:400px; text-align:center; }}
        h2 {{ color:{color}; margin-bottom:25px; font-size:24px; }}
        p {{ font-size:16px; }}
        a button {{ padding:14px; border:none; border-radius:8px; background-color:{color}; color:white; font-size:16px; cursor:pointer; margin-top:20px; }}
        a button:hover {{ background-color:{color if success else '#d32f2f'}; }}
        @media (max-width: 480px) {{ .card {{ padding:20px; }} h2 {{ font-size:20px; }} p, a button {{ font-size:14px; padding:12px; }} }}
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

# --- Routes ---
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
