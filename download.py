import os
import glob
import subprocess
from pathlib import Path
from fastapi import FastAPI, Query
from catbox import upload_to_catbox

app = FastAPI()
AUTHOR = "minatocodes"

COOKIE_FILE = "/tmp/cookies.txt"

def write_cookie_from_env():
    cookie_data = os.environ.get("COOKIE")
    if not cookie_data:
        return None
    cookie_data = cookie_data.replace("\r\n", "\n").replace("\r", "\n")
    Path(COOKIE_FILE).write_text(cookie_data, encoding="utf-8")
    os.chmod(COOKIE_FILE, 0o600)
    return COOKIE_FILE

@app.get("/api/download")
async def download(url: str, upload: bool = True):
    outdir = "/tmp"
    outtmpl = os.path.join(outdir, "%(title)s.%(ext)s")
    cookiefile = write_cookie_from_env()

    cmd = [
        "yt-dlp",
        "-f", "best[ext=mp4]/best",
        "-o", outtmpl,
        "--no-part",
        "--merge-output-format", "mp4",
        url
    ]
    if cookiefile:
        cmd.extend(["--cookies", cookiefile])

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {
            "success": False,
            "error": proc.stderr[:500],
            "author": AUTHOR
        }

    mp4s = glob.glob(os.path.join(outdir, "*.mp4"))
    if not mp4s:
        return {"success": False, "error": "No MP4 produced", "author": AUTHOR}
    latest = max(mp4s, key=os.path.getmtime)

    if upload:
        try:
            link = await upload_to_catbox(latest)
            return {"success": True, "url": link, "author": AUTHOR}
        except Exception as e:
            return {"success": True, "path": latest, "error": str(e), "author": AUTHOR}

    return {"success": True, "path": latest, "author": AUTHOR}
    
