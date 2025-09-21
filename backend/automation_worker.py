# backend/automation_worker.py
import asyncio
from playwright.async_api import async_playwright, TimeoutError

# The _login_to_facebook and verify_login functions are unchanged and correct.
async def _login_to_facebook(page, username, password):
    print(f"Attempting to log in as {username} on m.facebook.com...")
    await page.goto("https://m.facebook.com")
    await page.locator('input[name="email"]').fill(username)
    await page.locator('input[name="pass"]').fill(password)
    await page.get_by_role('button', name="Log In").click()
    print("Login submitted. Waiting for next page...")
    save_info_button = page.get_by_role("button", name="Not now")
    main_feed_locator = page.get_by_role("button", name="Make a Post on Facebook")
    try:
        task_save_info = asyncio.create_task(save_info_button.wait_for(state="visible", timeout=15000))
        task_main_feed = asyncio.create_task(main_feed_locator.wait_for(state="visible", timeout=15000))
        done, pending = await asyncio.wait([task_save_info, task_main_feed], return_when=asyncio.FIRST_COMPLETED)
        for task in pending: task.cancel()
        if task_save_info in done:
            print("Detected 'Save Info' screen. Clicking 'Not now'...")
            await save_info_button.click()
            await main_feed_locator.wait_for(state="visible", timeout=10000)
        elif task_main_feed in done:
            print("Landed directly on the main feed.")
        print("Login verification successful.")
    except TimeoutError as e:
        print("❌ Login verification failed.")
        await page.screenshot(path="login_verification_failed.png")
        print("Screenshot saved to 'login_verification_failed.png'")
        raise e

async def verify_login(username, password):
    # This function is not used in this test
    pass

async def create_post(username, password, post_content):
    """DEBUGGING SCRIPT TO FIND THE TEXTBOX LOCATOR."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(**p.devices['iPhone 13'])
        page = await context.new_page()
        try:
            await _login_to_facebook(page, username, password)
            print("Opening post composer...")
            await page.get_by_role("button", name="Make a Post on Facebook").click(force=True)

            # --- DEBUGGING STEP ---
            # The script will pause here with the composer open.
            print(">>> SCRIPT PAUSED: Use the Inspector to find the textbox locator. <<<")
            await page.pause()
            # --------------------

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            print("Debugging session finished. Closing browser.")
            await browser.close()

# --- STANDALONE TEST BLOCK ---
# This part of the script runs when you use the command 'python automation_worker.py'
if __name__ == "__main__":
    # 1. FILL IN YOUR CREDENTIALS HERE
    test_username = "61578973617715"
    test_password = "2HP4MBO31D"
    test_content = "test."

    if test_username == "YOUR_TEST_USERNAME":
        print("Please update the test credentials at the bottom of automation_worker.py")
    else:
        # 2. THIS COMMAND RUNS THE TEST
        asyncio.run(create_post(test_username, test_password, test_content))