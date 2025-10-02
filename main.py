from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pandas as pd
import os

app = FastAPI()

# Load CSV mapping
CSV_PATH = os.path.join(os.path.dirname(__file__), "file_map.csv")
df = pd.read_csv(CSV_PATH)
file_map = {str(k).strip().lower(): str(v).strip() for k, v in zip(df["userid"], df["fileid"])}

# Home page HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Employee Document Portal</title>
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #74ebd5, #ACB6E5);
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
    }
    .card {
        background-color: #fff;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        width: 350px;
        text-align: center;
        transition: transform 0.3s;
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .card img {
        width: 80px;
        margin-bottom: 20px;
    }
    .card h2 {
        margin-bottom: 25px;
        color: #333;
    }
    input[type=text] {
        width: 100%;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #ccc;
        margin-bottom: 20px;
        font-size: 16px;
    }
    button {
        width: 100%;
        padding: 12px;
        border: none;
        border-radius: 8px;
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        cursor: pointer;
        transition: background 0.3s;
    }
    button:hover {
        background-color: #45a049;
    }
    .download-link {
        margin-top: 20px;
        display: inline-block;
        background-color: #2196F3;
        color: white;
        padding: 12px 20px;
        text-decoration: none;
        border-radius: 8px;
        transition: background 0.3s;
    }
    .download-link:hover {
        background-color: #1976D2;
    }
</style>
</head>
<body>
<div class="card">
    <img src="https://via.placeholder.com/80" alt="Company Logo" />
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
        return HTMLResponse(f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display:flex; flex-direction:column; justify-content:center; align-items:center; height:100vh;">
            <h2 style="color:green;">✅ File ready for download</h2>
            <a class="download-link" href="{url}" target="_blank">Click here to download your document</a>
        </div>
        """)
    return HTMLResponse("<h3 style='color:red; text-align:center; margin-top:50px;'>❌ User ID not found or file inaccessible.</h3>", status_code=404)
