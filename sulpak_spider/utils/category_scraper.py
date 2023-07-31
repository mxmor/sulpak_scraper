from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

from dotenv import set_key
from pathlib import Path

def scrape_categories():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.set_window_size(1920, 1080)

    driver.get('https://sulpak.kz')

    driver.execute_script("document.elementFromPoint(0, 0).click();")

    wait = WebDriverWait(driver, 10)

    try:
        catalog_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'header__main-catalog-link')))
        catalog_button.click()
    except WebDriverException:
        menu_burger = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'header__main-menu-burger')))
        menu_burger.click()
        catalog_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'mobile__menu-close-js')))
        catalog_link.click()

    categories_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'header__catalog-left-menu-link')))

    categories = [category.get_attribute('href') for category in categories_elements]

    categories_string = ",".join(categories)

    env_file_path = Path(__file__).parent.parent / ".env"
    env_file_path.touch(mode=0o600, exist_ok=False)
    set_key(dotenv_path=env_file_path, key_to_set="SULPAK_CATEGORIES", value_to_set=categories_string)

    driver.quit()