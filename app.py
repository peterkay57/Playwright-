from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import asyncio
from urllib.parse import urlparse

app = FastAPI(title="Playwright Crawler API")

# Global browser instance (reused across requests)
browser = None
playwright_instance = None

async def get_browser():
    global browser, playwright_instance
    if browser is None:
        playwright_instance = await async_playwright().start()
        browser = await playwright_instance.chromium.launch(headless=True)
    return browser

async def extract_links(page, base_url):
    """Extract all internal Wikipedia links from a fully rendered page."""
    await page.wait_for_load_state("networkidle")
    
    links = await page.evaluate('''() => {
        const anchors = document.querySelectorAll('a');
        const hrefs = new Set();
        for (const a of anchors) {
            let href = a.href;
            if (href && href.startsWith('https://en.wikipedia.org/wiki/') && !href.includes(':') && !href.includes('#')) {
                hrefs.add(href);
            }
        }
        return Array.from(hrefs);
    }''')
    return links

async def scrape_page(page, url):
    """Scrape a single page and return its data."""
    await page.goto(url, wait_until="networkidle")
    content = await page.content()
    title = await page.title()
    return {"url": url, "title": title, "html": content[:10000], "success": True}

@app.get("/crawl")
async def deep_crawl(start_url: str, max_pages: int = 20):
    """Deep crawl starting from a URL (follows internal Wikipedia links)."""
    browser = await get_browser()
    context = await browser.new_context()
    page = await context.new_page()
    
    visited = set()
    queue = [start_url]
    results = []
    
    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        
        try:
            scraped = await scrape_page(page, url)
            if scraped.get("success"):
                visited.add(url)
                results.append(scraped)
                
                # Extract new links from the same domain
                new_links = await extract_links(page, url)
                domain = urlparse(start_url).netloc
                for link in new_links:
                    if domain in link and link not in visited and link not in queue:
                        queue.append(link)
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    
    await page.close()
    await context.close()
    
    return {
        "start_url": start_url,
        "pages_crawled": len(visited),
        "max_pages": max_pages,
        "results": results
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
