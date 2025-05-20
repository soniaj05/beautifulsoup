from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# URL and Chrome options
url = 'https://riseconf.com/investors'
options = Options()
options.add_argument('--headless=new')  # Headless mode
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# Initialize WebDriver
driver = webdriver.Chrome(options=options)
driver.get(url)

# List to store all investor data
all_investors = []

try:
    # Wait for initial page load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.speaker__content__inner"))
    )

    # Function to extract investor data
    def extract_investors():
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        investors = soup.find_all('div', class_='speaker__content__inner')
        return [investor.get_text(strip=True) for investor in investors]

    # Get initial investors (first 24)
    initial_investors = extract_investors()
    all_investors.extend(initial_investors)
    print(f"Initial investors captured: {len(initial_investors)}")

    # Keep clicking "View More" until no more appear
    while True:
        try:
            # Find and click the "View More" button
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-white-green.full-width"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", button)
            driver.execute_script("arguments[0].click();", button)

            # Wait for new investors to load
            WebDriverWait(driver, 10).until(
                lambda d: len(extract_investors()) > len(all_investors)
            )

            # Extract new investors and add to list
            new_investors = extract_investors()
            new_investors = [inv for inv in new_investors if inv not in all_investors]  # Avoid duplicates
            all_investors.extend(new_investors)
            print(f"Added {len(new_investors)} more investors")

        except Exception as e:
            print(f"No more 'View More' button or content to load: {e}")
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()

# Save to CSV
print(f"\nTotal investors found: {len(all_investors)}")
df = pd.DataFrame({'Investor Name': all_investors})
df.to_csv('investors_list.csv', index=False, encoding='utf-8-sig')
print("\nInvestor data saved to 'investor_list.csv'")