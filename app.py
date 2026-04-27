from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import asyncio
import random
import json
import requests

app = FastAPI(title="Smart Playwright API")

# ========== GEMINI API KEY (YOUR KEY) ==========
GEMINI_API_KEY = "AIzaSyAuLs0FZ7O65fzuvQbN_BdTb4dVHjC2yHw"

# ========== HTML WEB INTERFACE ==========
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Scraper - AI Powered</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background: #1a1a2e;
            color: white;
        }
        input, textarea, button {
            padding: 12px;
            margin: 10px 0;
            border-radius: 8px;
            border: none;
            font-size: 16px;
        }
        input, textarea {
            width: 100%;
            background: #0f3460;
            color: white;
        }
        textarea {
            height: 80px;
        }
        button {
            background: #e94560;
            color: white;
            cursor: pointer;
        }
        pre {
            background: #0f3460;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>🤖 Smart Scraper</h1>
    <p>Enter a URL and tell me what to extract</p>
    
    <input type="text" id="url" placeholder="URL (e.g., https://news.ycombinator.com)">
    <textarea id="command" placeholder="Command (e.g., extract top 5 headlines with points)"></textarea>
    <button onclick="scrape()">Scrape & Extract</button>
    
    <div id="loading" style="display:none;">Scraping and analyzing...</div>
    <pre id="result">Waiting...</pre>

    <script>
        async function scrape() {
            const url = document.getElementById('url').value;
            const command = document.getElementById('command').value;
            if (!url || !command) {
                alert('Please enter both URL and command');
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').innerText = 'Processing...';
            
            try {
                const response = await fetch(`/smart-scrape?url=${encodeURIComponent(url)}&command=${encodeURIComponent(command)}`);
                const data = await response.json();
                document.getElementById('result').innerText = JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').innerText = 'Error: ' + error.message;
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

@app.get("/smart-scrape")
async def smart_scrape(url: str, command: str):
    """Scrape any URL and extract what the user asks for using Gemini AI"""
    
    # ========== STEP 1: Scrape the webpage ==========
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            title = await page.title()
            await browser.close()
    except Exception as e:
        return {
            "url": url,
            "command": command,
            "error": f"Failed to scrape: {str(e)}",
            "extracted": []
        }
    
    # ========== STEP 2: Send to Gemini for extraction ==========
    try:
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        prompt = f"""
User command: {command}

Webpage title: {title}
Webpage content (first 5000 characters):
{content[:5000]}

Extract exactly what the user asked for from the content above.
Return ONLY valid JSON. No explanations, no extra text.
Example output format: [{{"item1": "value1", "item2": "value2"}}]
If nothing found, return [].
"""
        
        response = requests.post(
            gemini_url,
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            },
            timeout=60
        )
        
        result = response.json()
        extracted_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "[]")
        
        # Clean up markdown code blocks if present
        extracted_text = extracted_text.replace("```json", "").replace("```", "").strip()
        
        try:
            extracted_data = json.loads(extracted_text)
        except:
            extracted_data = {"raw_output": extracted_text, "error": "Could not parse as JSON"}
            
    except Exception as e:
        extracted_data = {"error": f"AI extraction failed: {str(e)}"}
    
    return {
        "url": url,
        "command": command,
        "page_title": title,
        "extracted": extracted_data
    }

@app.get("/health")
def health():
    return {"status": "ok"}
