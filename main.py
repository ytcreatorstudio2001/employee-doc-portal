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
HOME_PAGE = """
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
    .card:hover { transform: translateY(-5px); }
    .card img { width: 80px; margin-bottom: 20px; }
    .card h2 { margin-bottom: 25px; color: #333; }
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
    button:hover { background-color: #45a049; }
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

# Generic page template for download & error pages
def page_template(title, message, button_text=None, button_link=None, success=True):
    color = "#4CAF50" if success else "#f44336"
    button_html = ""
    if button_text and button_link:
        button_html = f'<a href="{button_link}" style="margin-top:20px; text-decoration:none;"><button>{button_text}</button></a>'
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #74ebd5, #ACB6E5);
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
            margin:0;
        }}
        .card {{
            background-color:#fff;
            padding:40px;
            border-radius:15px;
            box-shadow:0 10px 25px rgba(0,0,0,0.2);
            width:400px;
            text-align:center;
        }}
        h2 {{ color:{color}; margin-bottom:25px; }}
        a button {{
            padding:12px 20px;
            border:none;
            border-radius:8px;
            background-color:{color};
            color:white;
            font-size:16px;
            cursor:pointer;
            transition:background 0.3s;
        }}
        a button:hover {{ background-color:{color if success else '#d32f2f'}; }}
        a {{ text-decoration:none; }}
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
