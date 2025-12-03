import httpx

async def upload_to_catbox(file_path: str) -> str:
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload"}
    files = {"fileToUpload": open(file_path, "rb")}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=data, files=files)
        r.raise_for_status()
        return r.text.strip()
      
