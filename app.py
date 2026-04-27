from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import asyncio

app = FastAPI(title="Playwright API")

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Playwright Scraper</title>
    <style>
        body{font-family:Arial;max-width:800px;margin:50px auto;padding:20px;background:#1a1a2e;color:white;}
        input,button{padding:12px;margin:10px 0;border-radius:8px;border:none;font-size:16px;}
        input{width:70%;background:#0f3460;color:white;}
        button{background:#e94560;color:white;cursor:pointer;}
        pre{background:#0f3460;padding:15px;border-radius:8px;overflow-x:auto;}
    </style>
</head>
<body>
    <h1>Playwright Web Scraper</h1>
    <input type="text" id="url" placeholder="Enter URL">
    <button onclick="scrape()">Scrape</button>
    <pre id="result">Waiting...</pre>
    <script>
        async function scrape() {
            const url = document.getElementById('url').value;
            if(!url) return;
            document.getElementById('result').innerText = 'Scraping...';
            const res = await fetch(`/render?url=${encodeURIComponent(url)}`);
            const data = await res.json();
            document.getElementById('result').innerText = JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
"""

@app.get("/ui", response_class=HTMLResponse)
async def ui():
    return HTMLResponse(content=HTML_PAGE)

@app.get("/render")
async def render(url: str):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            title = await page.title()
            await browser.close()
            return {"url": url, "title": title, "html": content[:10000], "success": True}
    except Exception as e:
        return {"url": url, "error": str(e), "success": False}

@app.get("/health")
def health():
    return {"status": "ok"}
