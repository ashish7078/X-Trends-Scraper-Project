import os
import time
import socket
import undetected_chromedriver  as uc
import django
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv

# -----------------------------
#  Django + Env Setup
# -----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xtrends_backend.settings")
django.setup()

from trends.models import TrendRun  # Import after django.setup()

load_dotenv()
X_EMAIL = os.getenv("X_EMAIL")
X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")


# -----------------------------
#  Driver Setup with Options
# -----------------------------
def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)
    return driver


# -----------------------------
#  Login and Save Cookies
# -----------------------------
def login_and_save_cookies(driver):
    driver.get("https://x.com/login")
    time.sleep(3)

    # Enter email
    email_field = driver.find_element(By.NAME, "text")
    email_field.send_keys(X_EMAIL)
    email_field.send_keys(Keys.RETURN)
    time.sleep(3)

    # Enter username only if asked
    try:
        username_field = driver.find_element(By.NAME, "text")
        username_field.send_keys(X_USERNAME)
        username_field.send_keys(Keys.RETURN)
        time.sleep(3)
    except:
        print("⚠ Username step skipped")

    # Enter password
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(X_PASSWORD)
    password_field.send_keys(Keys.RETURN)
    time.sleep(5)

    # Save cookies
    cookies = driver.get_cookies()
    with open("x_cookies.json", "w") as f:
        json.dump(cookies, f)
    print("💾 Cookies saved for future sessions!")

    return driver


# -----------------------------
#  Load Driver with Cookies
# -----------------------------
def get_driver_with_session():
    driver = create_driver()
    driver.get("https://x.com/")

    if os.path.exists("x_cookies.json"):
        try:
            with open("x_cookies.json", "r") as f:
                cookies = json.load(f)
            for cookie in cookies:
                # Selenium requires domain to be set correctly
                if "sameSite" in cookie:
                    if cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                        cookie.pop("sameSite")
                driver.add_cookie(cookie)
            driver.get("https://x.com/explore")
            print("✅ Logged in using cookies!")
            return driver
        except Exception as e:
            print("⚠ Failed to load cookies, falling back to login:", e)

    # If cookies don’t exist or fail → do normal login
    driver = login_and_save_cookies(driver)
    print("✅ Logged in with credentials!")
    return driver


# -----------------------------
#  Scrape Top Trends
# -----------------------------
def fetch_top_trends(driver):
    driver.get("https://x.com/explore")
    time.sleep(5)

    opened_div = driver.find_element(
        By.XPATH,
        '//div[@aria-label="Timeline: Explore"]//div[@data-testid="cellInnerDiv"][6]',
    )

    next_five_divs = opened_div.find_elements(
        By.XPATH,
        'following-sibling::div[@data-testid="cellInnerDiv"][position() <= 5]',
    )

    texts = [div.text for div in next_five_divs if div.text.strip()]
    trend_names = [t.split("\n")[1] if "\n" in t else t for t in texts]

    return trend_names[:5]


# -----------------------------
#  Main Runner
# -----------------------------
def main():
    driver = get_driver_with_session()

    trends = fetch_top_trends(driver)
    print("🔥 Top 5 Trends:", trends)
    driver.quit()
    return trends
