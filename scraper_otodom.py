import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import json

def setup_driver():
    """Sets up a headless Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("WebDriver setup successful.")
    except Exception as e:
        print(f"Error during WebDriver setup: {e}")
        raise e
    return driver

def scrape_otodom_listings(target_url, max_pages_to_scrape=2):
    """
    Scrapes apartment listings from Otodom.pl using Selenium and BeautifulSoup.
    """
    listings_data = []
    driver = setup_driver()
    current_page_num = 1

    try:
        print(f"Navigating to {target_url} with Selenium...")
        driver.get(target_url)
        time.sleep(3)

        print("Attempting to handle cookie consent banner...")
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            print("Clicked cookie accept button.")
            time.sleep(2)
        except Exception as e_cookie:
            print(f"Cookie accept button not found or not clickable: {str(e_cookie).splitlines()[0]}.")
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                print("Sent Escape key to close potential overlays.")
                time.sleep(1)
            except Exception as e_escape:
                print(f"Failed to send escape key: {e_escape}")

        while current_page_num <= max_pages_to_scrape:
            print(f"\nScraping page {current_page_num}...")

            try:
                print("Waiting for listing items to be present on the page...")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-cy='listing-item']"))
                )
                print("Listing items found.")
            except Exception as e_wait:
                print(f"Timeout waiting for listing items on page {current_page_num}: {e_wait}")
                break

            for i in range(1, 5):
                driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {i/4});")
                time.sleep(1.5)
            time.sleep(3)

            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            listings_on_page = soup.select('article[data-cy="listing-item"]')
            print(f"Found {len(listings_on_page)} listings on page {current_page_num}.")

            if not listings_on_page:
                if current_page_num == 1:
                     print("No listings found on the first page. Check selectors or page structure.")
                else:
                    print(f"No listings found on page {current_page_num}. Likely end of results.")
                break

            for item_html in listings_on_page:
                title, price, price_czynsz, location_str, rooms, area, link = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

                link_tag = item_html.select_one('a[data-cy="listing-item-link"]')
                if link_tag and link_tag.has_attr('href'):
                    link_href = link_tag['href']
                    link = "https://www.otodom.pl" + link_href if not link_href.startswith('http') else link_href

                title_tag = item_html.select_one('[data-cy="listing-item-title"]')
                if title_tag:
                    title = title_tag.get_text(strip=True)

                # Price (Best Effort)
                price_tag_primary = item_html.select_one('div[data-cy="card-price"] span:first-of-type')
                if not price_tag_primary:
                    price_tag_primary = item_html.select_one('span.css-rmqm02.eclomwz0') # class from previous analysis

                if price_tag_primary:
                    price_text = price_tag_primary.get_text(strip=True)
                    if "zapytaj" in price_text.lower():
                        price = "Zapytaj o cenę"
                    else:
                        match = re.search(r'([\d\s,]+)zł', price_text.replace('\xa0', ''))
                        if match:
                            price = match.group(1).strip().replace(' ', '') + " zł"
                        else:
                            price = price_text

                # Czynsz (Rent Supplement - Best Effort)
                additional_rent_tag = item_html.find("span", string=re.compile(r'^\+\s*([\d\s,]+)\s*zł\s*(czynsz|dodatkowo|media)', re.IGNORECASE))
                if additional_rent_tag:
                    match_czynsz = re.search(r'^\+\s*([\d\s,]+)\s*zł', additional_rent_tag.get_text(strip=True).replace('\xa0', ''), re.IGNORECASE)
                    if match_czynsz:
                        price_czynsz = match_czynsz.group(1).strip().replace(' ', '') + " zł"

                # Location (Best Effort)
                location_tag = item_html.select_one('p[data-cy="listing-item-location"]')
                if location_tag:
                    location_str = location_tag.get_text(strip=True)

                # Rooms & Area (Reliable)
                attributes_container = item_html.select_one("div[data-cy='listing-item-attributes-container'], div[role='group']")
                if not attributes_container:
                    attributes_container = item_html

                room_tag = attributes_container.find(["span","div","li"], string=re.compile(r'^\d+\s*(pokoj|pokoje|pokoi|kawalerka)\b', re.I))
                if room_tag: rooms = room_tag.get_text(strip=True)

                area_tag = attributes_container.find(["span","div","li"], string=re.compile(r'\d+([,.]\d+)?\s*m²'))
                if area_tag and "zł/m²" not in area_tag.get_text(strip=True):
                    area = area_tag.get_text(strip=True)

                listings_data.append({
                    "title": title,
                    "price": price,
                    "additional_rent": price_czynsz,
                    "location": location_str,
                    "rooms": rooms,
                    "area": area,
                    "link": link
                })

            if current_page_num < max_pages_to_scrape:
                try:
                    print("Looking for 'next page' button...")
                    next_page_button_selector = "button[data-cy='pagination.next-page'], ul[data-cy='pagination.buttons-list'] li:last-child > button, ul[data-cy='pagination.buttons-list'] li:last-child > a"
                    next_page_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, next_page_button_selector))
                    )

                    ref_elements_before_click = driver.find_elements(By.CSS_SELECTOR, 'article[data-cy="listing-item"]')
                    ref_element_for_staleness = ref_elements_before_click[0] if ref_elements_before_click else None

                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", next_page_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", next_page_button)
                    print("'Next page' button clicked.")
                    current_page_num += 1

                    print("Waiting for page content to update (max 30s)...")
                    if ref_element_for_staleness:
                        WebDriverWait(driver, 30).until(EC.staleness_of(ref_element_for_staleness))
                    else:
                        print("No reference element for staleness check, using fixed time wait (10s).")
                        time.sleep(10)

                    WebDriverWait(driver, 25).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-cy='listing-item']"))
                    )
                    print("Next page appears to be loaded.")
                except Exception as e_next:
                    print(f"Pagination failed: {str(e_next).splitlines()[0]}")
                    break
            else:
                print("Reached max_pages_to_scrape limit.")
                break
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Closing WebDriver.")
        driver.quit()
    return listings_data

if __name__ == "__main__":
    OTODOM_URL = "https://www.otodom.pl/pl/oferty/wynajem/mieszkanie/katowice"

    print("Starting Otodom scraper...")
    # Scrape 2 pages as per final requirement
    scraped_data = scrape_otodom_listings(OTODOM_URL, max_pages_to_scrape=2)

    if scraped_data:
        print(f"\nSuccessfully scraped {len(scraped_data)} listings.")
        # Print details of the first 3-5 listings
        for i, listing in enumerate(scraped_data[:5]):
            print(f"\nListing {i+1}:")
            print(json.dumps(listing, indent=2, ensure_ascii=False))
    else:
        print("\nNo listings were scraped, or an error occurred before data collection.")
    print("\nScript finished.")
