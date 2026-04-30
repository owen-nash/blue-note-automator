import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def analyze_login():
    signin_url = os.getenv("PRESTO_SIGNIN_URL")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"Navigating to {signin_url}...")
        await page.goto(signin_url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)
        
        # Analyze inputs
        inputs = await page.evaluate('''() => {
            const elms = document.querySelectorAll('input');
            return Array.from(elms).map(e => ({
                type: e.type,
                name: e.name,
                id: e.id,
                placeholder: e.placeholder,
                className: e.className
            }));
        }''')
        print("Detected Inputs:", inputs)
        
        # Analyze buttons
        buttons = await page.evaluate('''() => {
            const elms = document.querySelectorAll('button');
            return Array.from(elms).map(e => ({
                type: e.type,
                text: e.innerText,
                className: e.className
            }));
        }''')
        print("Detected Buttons:", buttons)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_login())
