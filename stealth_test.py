from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync  # Import the stealth function

def test_scraper(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # APPLY STEALTH HERE:
        stealth_sync(page) 
        
        print(f"Navigating to {url} with stealth...")
        page.goto(url)
        
        # Save a screenshot to verify
        page.screenshot(path="stealth_screenshot.png")
        print("Done! Check 'stealth_screenshot.png'.")
        
        browser.close()

test_scraper("https://www.google.com")
