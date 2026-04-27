from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import asyncio
import json
import requests

app = FastAPI(title="Playwright API")

GEMINI_API_KEY = "AIzaSyAuLs0FZ7O65fzuvQbN_BdTb4dVHjC2yHw"

# HTML UI (same as before)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Playwright Scraper</title>
    <style>
        body{font-family:Arial;max-width:900px;margin:50px auto;padding:20px;background:#1a1a2e;color:white;}
        input,textarea,button{padding:12px;margin:10px 0;border-radius:8px;border:none;font-size:16px;}
        input,textarea{width:100%;background:#0f3460;color:white;}
        textarea{height:80px;}
        button{background:#e94560;color:white;cursor:pointer;}
        pre{background:#0f3460;padding:15px;border-radius:8px;overflow-x:auto;}
    </style>
</head>
<body>
    <h1>🤖 Smart Playwright Scraper</h1>
    <input type="text" id="url" placeholder="URL (e.g., https://www.bbc.com/news)">
    <textarea id="command" placeholder="Command (e.g., extract all article titles)"></textarea>
    <button onclick="smartScrape()">Scrape & Extract</button>
    <div id="loading" style="display:none;">Processing...</div>
    <pre id="result">Waiting...</pre>
    <script>
        async function smartScrape() {
            const url = document.getElementById('url').value;
            const command = document.getElementById('command').value;
            if (!url || !command) { alert('Please enter both'); return; }
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').innerText = 'Processing...';
            try {
                const res = await fetch(`/smart-scrape?url=${encodeURIComponent(url)}&command=${encodeURIComponent(command)}`);
                const data = await res.json();
                document.getElementById('result').innerText = JSON.stringify(data, null, 2);
            } catch (err) {
                document.getElementById('result').innerText = 'Error: ' + err.message;
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

@app.get("/ui", response_class=HTMLResponse)
async def ui():
    return HTMLResponse(content=HTML_PAGE)

# ========== SIMPLE SCRAPE (NO AI) ==========
@app.get("/render")
async def render(url: str):
    """Simple scrape – returns raw HTML (no AI)"""
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

# ========== AI‑POWERED SMART SCRAPE ==========
@app.get("/smart-scrape")
async def smart_scrape(url: str, command: str):
    """Scrape and use Gemini to extract exactly what the user asks for"""
    # 1. Scrape with Playwright
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            title = await page.title()
            await browser.close()
    except Exception as e:
        return {"url": url, "command": command, "error": f"Scrape failed: {str(e)}", "extracted": []}
    
    # 2. Ask Gemini to extract the requested information
    try:
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        prompt = f"""
User command: {command}

Page title: {title}
Page content (first 5000 chars):
{content[:5000]}

Extract exactly what the user asked for. Return ONLY valid JSON.
Example: [{{"title": "...", "url": "..."}}]
If nothing found, return [].
"""
        resp = requests.post(gemini_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=60)
        result = resp.json()
        extracted_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "[]")
        extracted_text = extracted_text.replace("```json", "").replace("```", "").strip()
        try:
            extracted_data = json.loads(extracted_text)
        except:
            extracted_data = []
    except Exception as e:
        extracted_data = {"error": f"AI failed: {str(e)}"}
    
    return {"url": url, "command": command, "page_title": title, "extracted": extracted_data}

@app.get("/health")
def health():
    return {"status": "ok"}
