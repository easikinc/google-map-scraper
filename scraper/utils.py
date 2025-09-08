from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

def scrape_google_maps(query):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless for web app server
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    search_query = query
    google_maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}/"
    driver.get(google_maps_url)
    time.sleep(5)  # wait for page load

    possible_xpaths = [
        f'//*[@aria-label="Results for {search_query}"]',
    ]

    scrollable_div = None
    for xpath in possible_xpaths:
        try:
            scrollable_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            break
        except:
            continue

    if not scrollable_div:
        driver.quit()
        raise Exception("Results sidebar not found.")

    # Scroll sidebar
    for _ in range(20):  # scroll 20 times to load more results
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    business_cards = soup.find_all("div", class_="Nv2PK")  # update if DOM changes

    data = []
    for card in business_cards:
        raw_text = card.text
        
        name_match = re.match(r"^(.*?)\s{2,}", raw_text)
        business_name = name_match.group(1) if name_match else raw_text.split("  ")[0]
        
        phone_matches = re.findall(r'\b\d[\d\s]{7,}\d\b', raw_text)
        phone_number = phone_matches[0].replace("\u202f", "").strip() if phone_matches else ""
        
        address_match = re.search(r'·\s*(.*?)Open', raw_text)
        address = address_match.group(1).strip() if address_match else ""
        
        website = "Yes" if "Website" in raw_text else "No"
        
        email = ""  # no email available
        
        data.append({
            "Business Name": business_name,
            "Phone Number": phone_number,
            "Address": address,
            "Website": website,
            "Email": email
        })

    return data