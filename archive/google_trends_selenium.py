from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import yaml

# Load disease info from YAML
with open('src/config/diseases.yaml', 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

diseases = cfg['diseases']

# Set up the Chrome driver (update the path if needed)
driver = webdriver.Chrome()  # or webdriver.Chrome(executable_path='path/to/chromedriver')

try:
    for d in diseases:
        search_terms = d['trends_terms']
        for term in search_terms:
            print(f"Searching Google Trends for: {term}")
            driver.get("https://trends.google.com/trends/")
            time.sleep(3)
            search_box = driver.find_element(By.CSS_SELECTOR, "input[aria-label='Search term']")
            search_box.clear()
            search_box.send_keys(term)
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)
            # Try to find and click the download button
            try:
                download_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Download CSV']")
                download_button.click()
                print(f"Downloaded CSV for: {term}")
            except Exception as e:
                print(f"Could not download CSV for {term}: {e}")
            time.sleep(5)  # Wait for download to complete
finally:
    driver.quit()
