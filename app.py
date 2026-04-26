from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import asyncio

app = FastAPI(title="Playwright API", description="Render JavaScript-heavy websites")

# ========== PROFESSIONAL HTML WEB INTERFACE ==========
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartLinker Bot | Professional Web Scraper</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #a0a0b0;
            font-size: 1.1rem;
        }
        
        .badge {
            display: inline-block;
            background: rgba(102, 126, 234, 0.2);
            color: #667eea;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-top: 15px;
        }
        
        /* Main Card */
        .card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 30px;
            margin-bottom: 30px;
        }
        
        /* Input Section */
        .input-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            color: #c0c0d0;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }
        
        input {
            width: 100%;
            padding: 14px 18px;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }
        
        input::placeholder {
            color: #5a5a7a;
        }
        
        /* Button */
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 14px 32px;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        /* Stats Bar */
        .stats {
            display: flex;
            gap: 20px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        
        .stat-card {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            padding: 12px 20px;
            flex: 1;
            text-align: center;
        }
        
        .stat-card .label {
            font-size: 0.7rem;
            color: #7a7a9a;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-card .value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #667eea;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 10px;
        }
        
        .tab {
            padding: 8px 20px;
            background: transparent;
            border: none;
            color: #a0a0b0;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .tab.active {
            color: #667eea;
            border-bottom: 2px solid #667eea;
        }
        
        /* Result Box */
        .result-box {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 16px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .result-header h3 {
            color: #c0c0d0;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .copy-btn {
            background: rgba(102, 126, 234, 0.2);
            border: none;
            padding: 5px 12px;
            border-radius: 8px;
            color: #667eea;
            cursor: pointer;
            font-size: 0.8rem;
        }
        
        pre {
            background: rgba(0, 0, 0, 0.5);
            padding: 15px;
            border-radius: 12px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #d0d0e0;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            max-height: 400px;
            overflow-y: auto;
        }
        
        /* Loading */
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(102, 126, 234, 0.3);
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: #5a5a7a;
            font-size: 0.8rem;
            margin-top: 30px;
        }
        
        /* Example Links */
        .examples {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        
        .example-link {
            background: rgba(102, 126, 234, 0.15);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            color: #a0a0b0;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .example-link:hover {
            background: rgba(102, 126, 234, 0.3);
            color: white;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 2rem; }
            .card { padding: 20px; }
            .stats { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 SmartLinker Bot</h1>
            <p>Professional Web Scraper & Render Engine</p>
            <div class="badge">⚡ Powered by Playwright | JavaScript Rendering</div>
        </div>
        
        <div class="card">
            <div class="input-group">
                <label>🌐 Enter Website URL</label>
                <input type="text" id="url" placeholder="https://example.com / https://react-app.com / https://any-website.com">
            </div>
            
            <div class="examples">
                <span class="example-link" onclick="setUrl('https://example.com')">📖 Example.com</span>
                <span class="example-link" onclick="setUrl('https://news.ycombinator.com')">💬 Hacker News</span>
                <span class="example-link" onclick="setUrl('https://github.com/trending')">🐙 GitHub Trending</span>
                <span class="example-link" onclick="setUrl('https://www.bbc.com/news')">📰 BBC News</span>
            </div>
            
            <button class="btn" id="scrapeBtn" onclick="scrape()">🚀 Render & Scrape</button>
        </div>
        
        <div class="card" id="statsCard" style="display: none;">
            <div class="stats">
                <div class="stat-card"><div class="label">URL</div><div class="value" id="statUrl">-</div></div>
                <div class="stat-card"><div class="label">TITLE</div><div class="value" id="statTitle">-</div></div>
                <div class="stat-card"><div class="label">CONTENT SIZE</div><div class="value" id="statSize">-</div></div>
            </div>
        </div>
        
        <div class="card">
            <div class="tabs">
                <button class="tab active" onclick="showTab('html')">📄 HTML Content</button>
                <button class="tab" onclick="showTab('json')">📋 JSON Raw</button>
            </div>
            
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p style="color: #a0a0b0;">Rendering page... This may take 10-30 seconds</p>
            </div>
            
            <div id="htmlResult" class="result-box" style="display: none;">
                <div class="result-header">
                    <h3>📄 Rendered HTML Preview</h3>
                    <button class="copy-btn" onclick="copyToClipboard('html')">📋 Copy</button>
                </div>
                <pre id="htmlContent"></pre>
            </div>
            
            <div id="jsonResult" class="result-box" style="display: none;">
                <div class="result-header">
                    <h3>📋 JSON Response</h3>
                    <button class="copy-btn" onclick="copyToClipboard('json')">📋 Copy</button>
                </div>
                <pre id="jsonContent"></pre>
            </div>
        </div>
        
        <div class="footer">
            <p>SmartLinker Bot | Renders JavaScript-heavy websites (React, Vue, Angular, SPA)</p>
            <p>⚡ API endpoint: <code style="background:rgba(0,0,0,0.3);padding:2px 6px;border-radius:4px;">/render?url=YOUR_URL</code></p>
        </div>
    </div>

    <script>
        let currentData = null;
        
        function setUrl(url) {
            document.getElementById('url').value = url;
        }
        
        async function scrape() {
            const url = document.getElementById('url').value;
            if (!url) {
                alert('Please enter a URL');
                return;
            }
            
            const btn = document.getElementById('scrapeBtn');
            const loading = document.getElementById('loading');
            const htmlResult = document.getElementById('htmlResult');
            const jsonResult = document.getElementById('jsonResult');
            const statsCard = document.getElementById('statsCard');
            
            btn.disabled = true;
            btn.textContent = '⏳ Rendering...';
            loading.style.display = 'block';
            htmlResult.style.display = 'none';
            jsonResult.style.display = 'none';
            statsCard.style.display = 'none';
            
            try {
                const response = await fetch(`/render?url=${encodeURIComponent(url)}`);
                const data = await response.json();
                currentData = data;
                
                // Update stats
                document.getElementById('statUrl').textContent = data.url || '-';
                document.getElementById('statTitle').textContent = data.title ? data.title.substring(0, 50) : '-';
                document.getElementById('statSize').textContent = data.html_length ? data.html_length.toLocaleString() + ' chars' : '-';
                statsCard.style.display = 'block';
                
                // Show HTML content
                const htmlPreview = data.html ? data.html.substring(0, 5000) : 'No content extracted';
                document.getElementById('htmlContent').textContent = htmlPreview + (data.html && data.html.length > 5000 ? '\n\n... (truncated, full content available via API)' : '');
                
                // Show JSON
                document.getElementById('jsonContent').textContent = JSON.stringify(data, null, 2);
                
                htmlResult.style.display = 'block';
                jsonResult.style.display = 'block';
                
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                btn.disabled = false;
                btn.textContent = '🚀 Render & Scrape';
                loading.style.display = 'none';
            }
        }
        
        function showTab(tab) {
            const htmlResult = document.getElementById('htmlResult');
            const jsonResult = document.getElementById('jsonResult');
            const tabs = document.querySelectorAll('.tab');
            
            tabs.forEach(t => t.classList.remove('active'));
            
            if (tab === 'html') {
                htmlResult.style.display = 'block';
                jsonResult.style.display = 'none';
                tabs[0].classList.add('active');
            } else {
                htmlResult.style.display = 'none';
                jsonResult.style.display = 'block';
                tabs[1].classList.add('active');
            }
        }
        
        function copyToClipboard(type) {
            let content = '';
            if (type === 'html') {
                content = document.getElementById('htmlContent').textContent;
            } else {
                content = document.getElementById('jsonContent').textContent;
            }
            navigator.clipboard.writeText(content);
            alert('Copied to clipboard!');
        }
        
        document.getElementById('url').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                scrape();
            }
        });
    </script>
</body>
</html>
"""

@app.get("/ui", response_class=HTMLResponse)
async def ui():
    return HTMLResponse(content=HTML_PAGE)

# ========== RENDER ENDPOINT ==========
@app.get("/render")
async def render(url: str):
    """
    Render a JavaScript-heavy webpage and return the HTML
    Example: /render?url=https://example.com
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Block unnecessary resources for faster loading
            async def block_resources(route):
                if route.request.resource_type in ["image", "font", "media"]:
                    await route.abort()
                else:
                    await route.continue_()
            await page.route("**/*", block_resources)
            
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            title = await page.title()
            await browser.close()
            
            return {
                "url": url,
                "title": title,
                "html": content[:10000],
                "html_length": len(content),
                "success": True
            }
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "success": False
        }

# ========== ROOT ENDPOINT ==========
@app.get("/")
def root():
    return {"message": "Playwright API is running. Use /render?url=YOUR_URL or go to /ui for web interface"}

# ========== HEALTH ENDPOINT ==========
@app.get("/health")
def health():
    return {"status": "ok"}