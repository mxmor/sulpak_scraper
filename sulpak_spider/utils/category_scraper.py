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

    # Set the window size
    driver.set_window_size(1920, 1080)

    # Navigate to the page
    driver.get('https://sulpak.kz')

    driver.execute_script("document.elementFromPoint(0, 0).click();")

    # Wait for the page to load completely
    wait = WebDriverWait(driver, 10)

    try:
        # Click the catalog button to load the categories
        catalog_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'header__main-catalog-link')))
        catalog_button.click()
    except WebDriverException:
        # If the catalog button can't be clicked, click the menu burger button
        menu_burger = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'header__main-menu-burger')))
        menu_burger.click()
        # Then, click on the 'header__catalog-link-js' element
        catalog_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'mobile__menu-close-js')))
        catalog_link.click()

    # Find all categories
    categories_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'header__catalog-left-menu-link')))

    # Extract href attribute of each category link and print them
    categories = [category.get_attribute('href') for category in categories_elements]

    # Convert the list to a string
    categories_string = ",".join(categories)

    env_file_path = Path(__file__).parent.parent / ".env"
    # Create the file if it does not exist.
    env_file_path.touch(mode=0o600, exist_ok=False)
    # Save some values to the file.
    set_key(dotenv_path=env_file_path, key_to_set="SULPAK_CATEGORIES", value_to_set=categories_string)

    # Close the driver
    driver.quit()