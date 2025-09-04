import subprocess
import shutil

def check_path(cmd):
    try:
        output = subprocess.check_output([cmd, "--version"], stderr=subprocess.STDOUT)
        return output.decode().strip()
    except Exception as e:
        return f"❌ {cmd} not found: {e}"

def main():
    print("=== Checking Chromium & Chromedriver ===")
    
    chromium_path = shutil.which("chromium") or shutil.which("chromium-browser")
    chromedriver_path = shutil.which("chromedriver")

    print(f"chromium path: {chromium_path}")
    print(f"chromedriver path: {chromedriver_path}")

    print(check_path("chromium") or check_path("chromium-browser"))
    print(check_path("chromedriver"))

if __name__ == "__main__":
    main()
