import os
import time
import json

def setup_django():
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xtrends_backend.settings")
    django.setup()
    global TrendRun
    from trends.models import TrendRun

def main():
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from dotenv import load_dotenv

    setup_django()
    load_dotenv()

    BROWSER_REMOTE = os.getenv("BROWSER_REMOTE_ENDPOINT", "").strip()
    X_EMAIL = os.getenv("X_EMAIL", "").strip()
    X_USERNAME = os.getenv("X_USERNAME", "").strip()
    X_PASSWORD = os.getenv("X_PASSWORD", "").strip()
    COOKIE_JSON_ENV = os.getenv("X_COOKIES_JSON", "").strip()

    if not BROWSER_REMOTE:
        raise RuntimeError("BROWSER_REMOTE_ENDPOINT not set")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Remote(command_executor=BROWSER_REMOTE, options=options)

    def save_cookies_to_env(cookies):
        try:
            print("saving cookies for manual copy to env (output suppressed in prod)")
        except Exception:
            pass

    def login_and_save_cookies(driver, email, username, password):
        driver.get("https://x.com/login")
        time.sleep(3)
        try:
            email_el = driver.find_element(By.NAME, "text")
            email_el.clear()
            email_el.send_keys(email)
            email_el.send_keys(Keys.RETURN)
            time.sleep(3)
        except Exception:
            pass
        try:
            username_el = driver.find_element(By.NAME, "text")
            if username:
                username_el.send_keys(username)
                username_el.send_keys(Keys.RETURN)
                time.sleep(2)
        except Exception:
            pass
        try:
            pwd_el = driver.find_element(By.NAME, "password")
            pwd_el.clear()
            pwd_el.send_keys(password)
            pwd_el.send_keys(Keys.RETURN)
            time.sleep(5)
        except Exception:
            pass
        try:
            cookies = driver.get_cookies()
            try:
                with open("/tmp/x_cookies.json", "w") as f:
                    json.dump(cookies, f)
            except Exception:
                pass
            save_cookies_to_env(cookies)
        except Exception:
            pass
        return driver

    def load_cookies_into_driver(driver):
        cookies = None
        if COOKIE_JSON_ENV:
            try:
                cookies = json.loads(COOKIE_JSON_ENV)
            except Exception:
                cookies = None
        else:
            try:
                with open("/tmp/x_cookies.json", "r") as f:
                    cookies = json.load(f)
            except Exception:
                cookies = None
        if not cookies:
            return False
        try:
            driver.get("https://x.com/")
            for cookie in cookies:
                if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                    cookie.pop("sameSite")
                try:
                    driver.add_cookie(cookie)
                except Exception:
                    pass
            driver.get("https://x.com/explore")
            time.sleep(2)
            return True
        except Exception:
            return False

    def get_driver_with_session(email, username, password):
        if load_cookies_into_driver(driver):
            return driver
        return login_and_save_cookies(driver, email, username, password)

    def fetch_top_trends(driver):
        driver.get("https://x.com/explore")
        time.sleep(5)
        try:
            opened_div = driver.find_element(By.XPATH, '//div[@aria-label="Timeline: Explore"]//div[@data-testid="cellInnerDiv"][6]')
            next_five_divs = opened_div.find_elements(By.XPATH, 'following-sibling::div[@data-testid="cellInnerDiv"][position() <= 5]')
            texts = [div.text for div in next_five_divs if div.text.strip()]
            trend_names = [t.split("\n")[1] if "\n" in t else t for t in texts]
            return trend_names[:5]
        except Exception:
            try:
                elems = driver.find_elements(By.XPATH, '//div[@data-testid="trend"]//span')
                topics = [e.text for e in elems if e.text.strip()]
                return topics[:5]
            except Exception:
                return []

    driver = get_driver_with_session(X_EMAIL, X_USERNAME, X_PASSWORD)
    trends = fetch_top_trends(driver)
    try:
        driver.quit()
    except Exception:
        pass

    while len(trends) < 5:
        trends.append("")

    client_ip = "0.0.0.0"
    obj = TrendRun.objects.create(
        trend1=trends[0],
        trend2=trends[1],
        trend3=trends[2],
        trend4=trends[3],
        trend5=trends[4],
        ip_address=client_ip
    )
    return obj
