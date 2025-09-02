import os
import sys
import time
import json
import django
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv

# -----------------------------
# Django + Env Setup
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xtrends_backend.settings")
django.setup()

from trends.models import TrendRun  # Import after django.setup()
load_dotenv()
X_EMAIL = os.getenv("X_EMAIL")
X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")

# -----------------------------
# Driver Setup with Options
# -----------------------------
def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)
    return driver

# -----------------------------
# Login and Save Cookies
# -----------------------------
def login_and_save_cookies(driver):
    driver.get("https://x.com/login")
    time.sleep(3)

    driver.find_element(By.NAME, "text").send_keys(X_EMAIL, Keys.RETURN)
    time.sleep(3)

    try:
        driver.find_element(By.NAME, "text").send_keys(X_USERNAME, Keys.RETURN)
        time.sleep(3)
    except:
        print("⚠ Username step skipped")

    driver.find_element(By.NAME, "password").send_keys(X_PASSWORD, Keys.RETURN)
    time.sleep(5)

    cookies = driver.get_cookies()
    with open("x_cookies.json", "w") as f:
        json.dump(cookies, f)
    return driver

def get_driver_with_session():
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
        except Exception as e:
            print("⚠ Failed to load cookies, falling back to login:", e)

    driver = login_and_save_cookies(driver)
    return driver

# -----------------------------
# Scrape Top Trends
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
# Main Runner with DB Save
# -----------------------------
def main():
    driver = get_driver_with_session()
    trends = fetch_top_trends(driver)
    driver.quit()

    # Ensure list has 5 items
    while len(trends) < 5:
        trends.append("")

    # Save to DB
    client_ip = "127.0.0.1"
    obj = TrendRun.objects.create(
        trend1=trends[0],
        trend2=trends[1],
        trend3=trends[2],
        trend4=trends[3],
        trend5=trends[4],
        ip_address=client_ip
    )

    print("🔥 Top 5 Trends saved to DB:", trends)
    return obj
