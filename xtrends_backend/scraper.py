import os
import time
import json

# -----------------------------
#  Django + Env Setup
# -----------------------------
def setup_django():
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xtrends_backend.settings")
    django.setup()
    global TrendRun
    from trends.models import TrendRun  # Import after setup

# -----------------------------
#  Main function exposed for Django
# -----------------------------
def main():
    # Import Selenium and undetected_chromedriver inside main
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    import undetected_chromedriver as uc
    from dotenv import load_dotenv

    # Django setup
    setup_django()

    # Load environment variables
    load_dotenv()
    email = os.getenv("X_EMAIL")
    username = os.getenv("X_USERNAME")
    password = os.getenv("X_PASSWORD")

    # -----------------------------
    #  Driver Setup
    # -----------------------------
    def create_driver():
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = uc.Chrome(options=options)
        return driver

    # -----------------------------
    #  Login & Cookies
    # -----------------------------
    def login_and_save_cookies(driver, email, username, password):
        driver.get("https://x.com/login")
        time.sleep(3)
        driver.find_element(By.NAME, "text").send_keys(email, Keys.RETURN)
        time.sleep(3)
        try:
            driver.find_element(By.NAME, "text").send_keys(username, Keys.RETURN)
            time.sleep(3)
        except:
            pass
        driver.find_element(By.NAME, "password").send_keys(password, Keys.RETURN)
        time.sleep(5)
        cookies = driver.get_cookies()
        with open("x_cookies.json", "w") as f:
            json.dump(cookies, f)
        return driver

    def get_driver_with_session(email, username, password):
        driver = create_driver()
        driver.get("https://x.com/")
        if os.path.exists("x_cookies.json"):
            try:
                with open("x_cookies.json", "r") as f:
                    cookies = json.load(f)
                for cookie in cookies:
                    if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                        cookie.pop("sameSite")
                    driver.add_cookie(cookie)
                driver.get("https://x.com/explore")
                return driver
            except:
                pass
        driver = login_and_save_cookies(driver, email, username, password)
        return driver

    # -----------------------------
    #  Scrape Trends
    # -----------------------------
    def fetch_top_trends(driver):
        driver.get("https://x.com/explore")
        time.sleep(5)
        opened_div = driver.find_element(
            By.XPATH,
            '//div[@aria-label="Timeline: Explore"]//div[@data-testid="cellInnerDiv"][6]'
        )
        next_five_divs = opened_div.find_elements(
            By.XPATH,
            'following-sibling::div[@data-testid="cellInnerDiv"][position() <= 5]'
        )
        texts = [div.text for div in next_five_divs if div.text.strip()]
        trend_names = [t.split("\n")[1] if "\n" in t else t for t in texts]
        return trend_names[:5]

    # -----------------------------
    #  Run scraper
    # -----------------------------
    driver = get_driver_with_session(email, username, password)
    trends = fetch_top_trends(driver)
    driver.quit()

    # Save to DB
    client_ip = "127.0.0.1"
    while len(trends) < 5:
        trends.append("")

    obj = TrendRun.objects.create(
        trend1=trends[0],
        trend2=trends[1],
        trend3=trends[2],
        trend4=trends[3],
        trend5=trends[4],
        ip_address=client_ip
    )
    return obj
