# Kbook/automation_test.py
import asyncio
from playwright.async_api import async_playwright, TimeoutError

## ------------------- IMPORTANT ------------------- ##
# Use a TEST Facebook account for this.
FACEBOOK_USERNAME = "61578973617715"
FACEBOOK_PASSWORD = "2HP4MBO31D"
## ------------------------------------------------- ##

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        print("Navigating to m.facebook.com...")
        await page.goto("https://m.facebook.com")
        await page.wait_for_load_state('domcontentloaded')

        print("Entering username and password...")
        await page.locator('input[name="email"]').fill(FACEBOOK_USERNAME)
        await page.locator('input[name="pass"]').fill(FACEBOOK_PASSWORD)

        print("Clicking login button...")
        await page.get_by_role('button', name="Log In").click()
        await page.wait_for_load_state('domcontentloaded')

        try:
            print("Checking for 'Save Info' pop-up...")
            save_button = page.get_by_role("button", name="Save")
            await save_button.click(timeout=5000)
            print("'Save Info' pop-up found and clicked.")
            await page.wait_for_load_state('domcontentloaded')
        except TimeoutError:
            print("No 'Save Info' pop-up appeared.")

        # Final verification
        try:
            print("Verifying login by looking for feed...")
            
            # CHANGED: Using the precise locator suggested by the error message.
            # This looks for a clickable element with the specific label "Make a Post on Facebook".
            feed_locator = page.get_by_role("button", name="Make a Post on Facebook")
            
            await feed_locator.wait_for(state="visible", timeout=10000)
            print("✅ Login Successful!")
        except TimeoutError:
            print("❌ Login Failed. Could not find the main feed.")
            await page.screenshot(path="login_failed.png")
            print("A new screenshot 'login_failed.png' was saved for debugging.")

        await asyncio.sleep(5)
        print("Closing browser.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())