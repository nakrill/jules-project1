import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

def extract_specific_details(driver, listing_url):
    """
    Extracts pet policy and lease term information from a single Otodom listing page.
    """
    pet_policy_info = "Information not found"
    lease_term_info = "Information not found"

    try:
        print(f"Navigating to detail page: {listing_url}")
        driver.get(listing_url)

        # Wait for main content sections to be potentially loaded
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-cy='advertDescription'], div[data-cy='advert-attributes'], main, #root"))
        )
        time.sleep(3) # Allow for JS rendering after initial load

        detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
        page_text_lower = detail_soup.get_text(" ", strip=True).lower()

        # --- Pet Policy Extraction ---
        # Look for specific data-testid attributes first
        pet_policy_label_element = detail_soup.find(attrs={"data-testid": "ad.additionalInformation.field.pets"})
        if pet_policy_label_element:
            value_element = pet_policy_label_element.find_next_sibling("div", attrs={"data-testid": "ad.additionalInformation.value"})
            if value_element:
                pet_policy_info = value_element.get_text(strip=True)

        if pet_policy_info == "Information not found": # If not found via data-testid, try broader text search
            pet_keywords_positive = ["zwierzęta akceptowane", "można z psem", "pet friendly", "zgoda na zwierzęta", "pupile mile widziane"]
            pet_keywords_negative = ["zwierzęta nieakceptowane", "zakaz zwierząt", "bez zwierząt", "zwierzęta niedozwolone"]

            description_div = detail_soup.select_one("div[data-cy='advertDescription']")
            search_text_pet = page_text_lower
            if description_div:
                search_text_pet = description_div.get_text(" ", strip=True).lower()

            for kw in pet_keywords_positive:
                if kw in search_text_pet:
                    pet_policy_info = f"Akceptowane (znaleziono: '{kw}')"
                    break
            if pet_policy_info == "Information not found": # Only search for negative if positive not found
                for kw in pet_keywords_negative:
                    if kw in search_text_pet:
                        pet_policy_info = f"Nieakceptowane (znaleziono: '{kw}')"
                        break

        # --- Lease Term Extraction ---
        lease_term_label_element = detail_soup.find(attrs={"data-testid": "ad.additionalInformation.field.leasePeriod"})
        if lease_term_label_element:
            value_element = lease_term_label_element.find_next_sibling("div", attrs={"data-testid": "ad.additionalInformation.value"})
            if value_element:
                lease_term_info = value_element.get_text(strip=True)

        if lease_term_info == "Information not found": # If not found via data-testid, try broader text search
            lease_keywords_patterns = [
                r"wynajem długoterminowy", r"najem okazjonalny", r"minimum (\d+\s+miesi(?:ące|ęcy|ąc))",
                r"minimum rok", r"umowa na czas (?:nie)?określony(?: na \d+ (?:miesięcy|lat))?",
                r"preferowany okres[:\s]*([\w\s]+)", r"okres umowy[:\s]*([\w\s]+)"
            ]
            found_lease_terms = []

            description_div_lease = detail_soup.select_one("div[data-cy='advertDescription']")
            search_text_lease = page_text_lower
            if description_div_lease:
                 search_text_lease = description_div_lease.get_text(" ", strip=True) # Keep original case for extraction

            for pattern in lease_keywords_patterns:
                match = re.search(pattern, search_text_lease, re.IGNORECASE)
                if match:
                    # If pattern has a capturing group for the value, use it, else use the whole match
                    extracted_value = match.group(1) if match.groups() and match.group(1) else match.group(0)
                    found_lease_terms.append(extracted_value.strip())

            if found_lease_terms:
                lease_term_info = "; ".join(list(set(found_lease_terms))) # Use set to avoid duplicates
            elif "okres najmu" in page_text_lower: # Generic check if the label exists but value wasn't picked by specific selector
                 lease_term_info = "Szczegóły w opisie (etykieta 'Okres najmu' znaleziona)"


    except Exception as e_detail:
        print(f"  Error scraping detail page {listing_url}: {str(e_detail).splitlines()[0]}")
        # In case of error, it will return the default "Information not found"

    return {"pet_policy_info": pet_policy_info, "lease_term_info": lease_term_info}


if __name__ == "__main__":
    # Example URL: https://www.otodom.pl/pl/oferta/sloneczne-mieszkanie-przy-parku-slaskim-ID4vuIh
    # This URL might become outdated. Replace with a current, valid Otodom listing URL if needed.
    SAMPLE_LISTING_URL = "https://www.otodom.pl/pl/oferta/sloneczne-mieszkanie-przy-parku-slaskim-ID4vuIh"

    # Check if a command-line argument (URL) is provided
    import sys
    if len(sys.argv) > 1:
        listing_url_to_scrape = sys.argv[1]
        print(f"Using URL from command line: {listing_url_to_scrape}")
    else:
        listing_url_to_scrape = SAMPLE_LISTING_URL
        print(f"Using default sample URL: {listing_url_to_scrape}")

    driver = None
    try:
        driver = setup_driver()
        # Handle cookie consent on the first navigation by the driver instance
        print(f"Initial navigation to {listing_url_to_scrape} to handle potential global popups/cookies...")
        driver.get(listing_url_to_scrape) # Initial navigation
        time.sleep(2)
        try:
            cookie_button = WebDriverWait(driver, 7).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            print("Clicked cookie accept button on initial load.")
            time.sleep(2)
        except Exception:
            print("No cookie button found on initial load, or already accepted. Proceeding.")


        details = extract_specific_details(driver, listing_url_to_scrape)
        print("\n--- Extracted Details ---")
        print(json.dumps(details, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"An error occurred in the main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("Closing WebDriver.")
            driver.quit()

    print("\nScript finished.")
