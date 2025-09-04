import os
import time
import psycopg2
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

X_EMAIL = os.getenv("X_EMAIL")
X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-software-rasterizer")
    driver = uc.Chrome(
        options=options,
        driver_executable_path="/usr/local/bin/chromedriver",
        browser_executable_path="/usr/bin/google-chrome",
        use_subprocess=True
    )
    return driver

def login(driver):
    driver.get("https://x.com/login")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "text")))
    driver.find_element(By.NAME, "text").send_keys(X_EMAIL, Keys.RETURN)
    time.sleep(2)

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "text")))
        driver.find_element(By.NAME, "text").send_keys(X_USERNAME, Keys.RETURN)
        time.sleep(2)
    except:
        print("⚠ Username step skipped")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
    driver.find_element(By.NAME, "password").send_keys(X_PASSWORD, Keys.RETURN)
    time.sleep(5)
    return driver

def get_driver_with_login():
    driver = create_driver()
    return login(driver)

def fetch_top_trends(driver):
    driver.get("https://x.com/explore")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Timeline: Explore"]'))
    )

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
        RETURNING id
    """, (trends[0], trends[1], trends[2], trends[3], trends[4], "127.0.0.1"))

    trend_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    print("🔥 Top 5 Trends saved to DB:", trends)
    return trend_id

def main():
    try:
        driver = get_driver_with_login()
        trends = fetch_top_trends(driver)
    except Exception as e:
        print("❌ Error during scraping:", e)
        trends = []
    finally:
        try:
            driver.quit()
        except:
            pass

    if trends:
        return save_to_db(trends)
    return None

if __name__ == "__main__":
    main()
