from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://pc.qq.com/category/c0.html")
    element_to_hover = page.locator("li")
    element_to_hover.hover()
    page.get_by_role("link", name="聊天（190）").click()
    page.locator("li").filter(has_text="微信 立即下载").locator("a").nth(1).click()
    with page.expect_download() as download1_info:
        page.get_by_text("直接下载").click()
    download1 = download1_info.value
    page.locator("img").first.click()
    page.locator("li").filter(has_text="QQ 立即下载").locator("a").nth(1).click()
    page.get_by_text("直接下载").click()
    with page.expect_download() as download2_info:
        page.locator("img").first.click()
    download2 = download2_info.value
    page.locator("li").filter(has_text="YY 语音 立即下载").locator("a").nth(1).click()
    with page.expect_download() as download3_info:
        page.get_by_text("直接下载").click()
    download3 = download3_info.value
    page.locator("img").first.click()
    page.locator("li").filter(has_text="斗鱼直播 立即下载").locator("a").nth(1).click()
    page.get_by_text("直接下载").click()
    with page.expect_download() as download5_info:
        page.get_by_text("直接下载").click()
    download5 = download5_info.value
    page.locator("img").first.click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
