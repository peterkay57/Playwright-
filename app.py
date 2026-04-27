from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import asyncio
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

app = FastAPI(title="Advanced Playwright API")

# ========== GLOBAL BROWSER (REUSED ACROSS REQUESTS) ==========
browser = None
playwright_instance = None

async def get_browser():
    global browser, playwright_instance
    if browser is None:
        playwright_instance = await async_playwright().start()
        browser = await playwright_instance.chromium.launch(headless=True)
    return browser

# ========== RESOURCE BLOCKING (SAVES MEMORY) ==========
async def route_handler(route):
    if route.request.resource_type in ["image", "font", "media", "stylesheet"]:
        await route.abort()
    else:
        await route.continue_()

# ========== SINGLE PAGE SCRAPE (REUSES BROWSER) ==========
async def scrape(url: str, wait_for: str = None):
    """Scrape a single URL - reuses browser, blocks resources, closes only tab"""
    browser = await get_browser()
    page = await browser.new_page()
    
    # Block unnecessary resources (saves memory)
    await page.route("**/*", route_handler)
    
    await page.goto(url, wait_until="networkidle")
    
    if wait_for:
        await page.wait_for_selector(wait_for, timeout=10000)
    
    content = await page.content()
    title = await page.title()
    
    await page.close()  # ✅ Close only the tab, keep browser alive
    
    return {"url": url, "title": title, "html": content[:10000], "success": True}

# ========== EXTRACT LINKS (FOR CRAWLING) ==========
async def extract_links(html: str, base_url: str):
    """Extract all links from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        full_url = urljoin(base_url, a['href'])
        if full_url.startswith(('http://', 'https://')):
            links.append(full_url)
    return list(set(links))

# ========== MULTIPLE URLS (CONCURRENT) ==========
async def scrape_multiple(urls):
    tasks = [scrape(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# ========== DEEP CRAWL (FOLLOWS LINKS) ==========
async def deep_crawl(start_url: str, max_pages: int = 50):
    visited = set()
    queue = [start_url]
    results = []
    
    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        
        # Scrape current page
        page_content = await scrape(url)
        if page_content.get("success"):
            visited.add(url)
            results.append(page_content)
            
            # Find new links from the same domain
            domain = urlparse(start_url).netloc
            links = await extract_links(page_content.get("html", ""), url)
            for link in links:
                if urlparse(link).netloc == domain and link not in visited and link not in queue:
                    queue.append(link)
    
    return results

# ========== LOGIN SESSION PERSISTENCE ==========
async def save_login_session(login_url: str, username: str, password: str):
    """Log in and save the session to auth.json"""
    browser = await get_browser()
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(login_url)
    await page.fill("#username", username)
    await page.fill("#password", password)
    await page.click("#login-button")
    await context.storage_state(path="auth.json")  # Save session
    await context.close()
    return {"success": True, "message": "Session saved to auth.json"}

async def use_saved_session():
    """Create a context with saved session"""
    browser = await get_browser()
    context = await browser.new_context(storage_state="auth.json")
    return context

# ========== FASTAPI ENDPOINTS ==========
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Advanced Playwright Scraper</title>
    <style>
        body{font-family:Arial;max-width:900px;margin:50px auto;padding:20px;background:#1a1a2e;color:white;}
        input,textarea,button{padding:12px;margin:10px 0;border-radius:8px;border:none;font-size:16px;}
        input,textarea{width:100%;background:#0f3460;color:white;}
        button{background:#e94560;color:white;cursor:pointer;}
        pre{background:#0f3460;padding:15px;border-radius:8px;overflow-x:auto;}
    </style>
</head>
<body>
    <h1>🕷️ Advanced Playwright Scraper</h1>
    
    <h3>Single URL Scrape</h3>
    <input type="text" id="url" placeholder="Enter URL">
    <button onclick="singleScrape()">Scrape</button>
    
    <h3>Multiple URLs (comma separated)</h3>
    <input type="text" id="urls" placeholder="url1, url2, url3">
    <button onclick="multipleScrape()">Scrape All</button>
    
    <h3>Deep Crawl (follows links)</h3>
    <input type="text" id="crawlUrl" placeholder="Starting URL">
    <input type="number" id="maxPages" placeholder="Max pages" value="20">
    <button onclick="deepCrawl()">Deep Crawl</button>
    
    <pre id="result">Waiting...</pre>

    <script>
        async function singleScrape() {
            const url = document.getElementById('url').value;
            if (!url) { alert('Enter URL'); return; }
            document.getElementById('result').innerText = 'Scraping...';
            const res = await fetch(`/scrape?url=${encodeURIComponent(url)}`);
            const data = await res.json();
            document.getElementById('result').innerText = JSON.stringify(data, null, 2);
        }
        
        async function multipleScrape() {
            const urls = document.getElementById('urls').value;
            if (!urls) { alert('Enter URLs'); return; }
            document.getElementById('result').innerText = 'Scraping...';
            const res = await fetch(`/scrape/multiple?urls=${encodeURIComponent(urls)}`);
            const data = await res.json();
            document.getElementById('result').innerText = JSON.stringify(data, null, 2);
        }
        
        async function deepCrawl() {
            const url = document.getElementById('crawlUrl').value;
            const maxPages = document.getElementById('maxPages').value;
            if (!url) { alert('Enter URL'); return; }
            document.getElementById('result').innerText = 'Deep crawling...';
            const res = await fetch(`/crawl?start_url=${encodeURIComponent(url)}&max_pages=${maxPages}`);
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

@app.get("/scrape")
async def scrape_single(url: str, wait_for: str = None):
    """Scrape a single URL"""
    return await scrape(url, wait_for)

@app.get("/scrape/multiple")
async def scrape_multiple_endpoint(urls: str, max_concurrent: int = 5):
    """Scrape multiple URLs concurrently"""
    url_list = [u.strip() for u in urls.split(",") if u.strip()][:max_concurrent]
    results = await scrape_multiple(url_list)
    return {"count": len(results), "results": results}

@app.get("/crawl")
async def deep_crawl_endpoint(start_url: str, max_pages: int = 20):
    """Deep crawl starting from a URL (follows links)"""
    results = await deep_crawl(start_url, max_pages)
    return {
        "start_url": start_url,
        "pages_crawled": len(results),
        "max_pages": max_pages,
        "results": results
    }

@app.get("/session/save")
async def save_session(login_url: str, username: str, password: str):
    """Save login session (for authenticated scraping)"""
    return await save_login_session(login_url, username, password)

@app.get("/health")
def health():
    return {"status": "ok"}
