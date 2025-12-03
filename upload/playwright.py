from playwright.sync_api import sync_playwright

def upload_file(path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://yourwebsite.com/login")
        page.fill("#username", "YOUR_USERNAME")
        page.fill("#password", "YOUR_PASSWORD")
        page.click("#login-button")

        page.goto("https://yourwebsite.com/upload-page")
        page.set_input_files("input[type='file']", path)
        page.click("#submit")
        browser.close()


