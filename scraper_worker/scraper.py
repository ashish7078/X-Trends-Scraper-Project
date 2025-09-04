import os
import time
import json
import psycopg2
# import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

X_EMAIL = os.getenv("X_EMAIL")
X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")  # NeonDB connection string

def create_driver():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

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

    return login_and_save_cookies(driver)

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

def save_to_db(trends):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    while len(trends) < 5:
        trends.append("")

    cur.execute("""
        INSERT INTO trends_trendrun (trend1, trend2, trend3, trend4, trend5, ip_address, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """, (trends[0], trends[1], trends[2], trends[3], trends[4], "127.0.0.1"))

    conn.commit()
    cur.close()
    conn.close()
    print("🔥 Top 5 Trends saved to DB:", trends)

def main():
    driver = get_driver_with_session()
    trends = fetch_top_trends(driver)
    driver.quit()
    save_to_db(trends)

if __name__ == "__main__":
    main()
