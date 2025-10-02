from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pandas as pd
import os

app = FastAPI()

# Load file_map.csv
CSV_PATH = os.path.join(os.path.dirname(__file__), "file_map.csv")
df = pd.read_csv(CSV_PATH)
file_map = {str(k).strip().lower(): str(v).strip() for k,v in zip(df["userid"], df["fileid"])}

# Login page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Employee Document Portal</title>
<style>
body { font-family: Arial; display:flex; align-items:center; justify-content:center; height:100vh; }
.card { padding:20px; box-shadow:0 4px 14px rgba(0,0,0,0.1); border-radius:10px; text-align:center; }
input[type=text] { width:100%; padding:10px; margin:10px 0; }
button { padding:10px 20px; cursor:pointer; }
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

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.post("/download")
async def download(userid: str = Form(...)):
    userid = userid.strip().lower()
    fileid = file_map.get(userid)
    if fileid:
        url = f"https://drive.google.com/uc?export=download&id={fileid}"
        # Return HTML with clickable link
        return HTMLResponse(f"""
        <h3>✅ File ready for download:</h3>
        <a href="{url}" target="_blank">Click here to download your document</a>
        """)
    return HTMLResponse("<h3 style='color:red;'>❌ User ID not found or file inaccessible.</h3>", status_code=404)
