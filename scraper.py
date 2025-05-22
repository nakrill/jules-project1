import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

def setup_driver():
    """Sets up a headless Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox") # Standard for running in containers/CI
    options.add_argument("--disable-dev-shm-usage") # Standard for running in containers/CI
    options.add_argument("--window-size=1920,1080") # Specify window size
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Automatically download and install the latest ChromeDriver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_gratka_listings_selenium(base_url, city_path="katowice", max_pages=1):
    """
    Scrapes apartment listings from Gratka.pl using Selenium and BeautifulSoup.
    """
    listings_data = []
    target_url = f"{base_url}/{city_path}/wynajem"
    driver = setup_driver()

    try:
        print(f"Navigating to {target_url} with Selenium...")
        driver.get(target_url)

        # Wait for a general page element to ensure basic loading.
        print("Waiting for the main listings container to load...")
        # --- Step 1: Handle Cookie Consent / Popups with more robust attempts ---
        print("Attempting to handle initial overlays (cookies, notifications)...")
        time.sleep(7) # Longer initial wait for overlays to fully appear

        # Try to click common "accept all" buttons for cookies
        cookie_accept_selectors_priority = [
            "button#onetrust-accept-btn-handler", # OneTrust specific
            "button[data-testid='accept-all-cookies-button']", # Common test ID
            "//button[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'akceptuję wszystkie')]", # More specific text
            "//button[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'zgadzam się na wszystko')]",
            "//button[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept all')]"
        ]
        
        popup_handled_flag = False
        for i, selector in enumerate(cookie_accept_selectors_priority):
            try:
                print(f"Trying priority cookie selector ({i+1}/{len(cookie_accept_selectors_priority)}): {selector}")
                element_to_click = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH if selector.startswith("//") else By.CSS_SELECTOR, selector))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", element_to_click) # Scroll into view
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", element_to_click)
                print(f"Clicked priority button with selector: {selector}")
                popup_handled_flag = True
                time.sleep(3) # Wait for action to take effect
                break
            except Exception as e_cookie:
                print(f"Priority cookie selector {selector} failed: {str(e_cookie).splitlines()[0]}")

        if not popup_handled_flag:
            print("Primary cookie accept methods failed. Trying secondary/generic methods...")
            # Fallback to more generic selectors if priority ones fail
            generic_accept_selectors = [
                "button[class*='accept']", "button[class*='consent']", "button[id*='accept']",
                "//button[contains(translate(lower-case(text()), 'ęóąśłżźćń', 'eoaslzzcn'), 'akcept')]",
                "//button[contains(translate(lower-case(text()), 'ęóąśłżźćń', 'eoaslzzcn'), 'zgod')]",
                "//button[contains(translate(lower-case(text()), 'ęóąśłżźćń', 'eoaslzzcn'), 'rozumiem')]",
            ]
            for i, selector in enumerate(generic_accept_selectors):
                try:
                    print(f"Trying generic popup selector ({i+1}/{len(generic_accept_selectors)}): {selector}")
                    element_to_click = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH if selector.startswith("//") else By.CSS_SELECTOR, selector))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", element_to_click)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", element_to_click)
                    print(f"Clicked generic button with selector: {selector}")
                    popup_handled_flag = True
                    time.sleep(2)
                    break
                except Exception as e_generic_cookie:
                    print(f"Generic cookie selector {selector} failed: {str(e_generic_cookie).splitlines()[0]}")
        
        if not popup_handled_flag:
            print("No popups explicitly handled by click. Trying to send 'Escape' key.")
            try:
                body_element = driver.find_element(By.TAG_NAME, "body")
                body_element.send_keys(webdriver.common.keys.Keys.ESCAPE)
                print("Sent 'Escape' key press.")
                time.sleep(1)
            except Exception as e_escape:
                print(f"Failed to send 'Escape' key: {e_escape}")


        # --- Step 2: Scroll Down Aggressively & Wait ---
        print("Scrolling down multiple times with pauses to trigger dynamic content...")
        for i in range(8): # Scroll even more times
            scroll_height_fraction = (i + 1) / 8
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {scroll_height_fraction});")
            print(f"Scroll {i+1}/8 to {scroll_height_fraction*100:.0f}% of page height.")
            time.sleep(2) # Wait for content to load after each scroll
        
        print("Finished scrolling. Performing a very long wait (20s) for any extremely delayed JS rendering...")
        time.sleep(20) 

        # --- Step 3: Attempt to find a general "Listings Area" container ---
        print("Attempting to find a general listings area container...")
        listings_area_html = None
        listings_area_selector_used = None
        
        # More diverse selectors for the main area that should contain listings
        possible_listings_area_selectors = [
            "div[data-cy='search.listing.regular']", # From a quick manual check of similar sites / common patterns
            "div[class*='listingResults']",
            "div[id*='listingContainer']",
            "section[class*='listingSection']",
            "main div[class*='feed']", # Common in modern web apps
            "div#mainResults"
        ]

        for selector in possible_listings_area_selectors:
            try:
                print(f"Trying listings area selector: {selector}")
                area_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if area_element.is_displayed():
                    print(f"Found visible listings area with selector: {selector}")
                    listings_area_html = area_element.get_attribute('innerHTML') # Get inner HTML of container
                    listings_area_selector_used = selector
                    break
                else:
                    print(f"Listings area for selector {selector} found but not visible.")
            except Exception as e_area:
                print(f"Selector {selector} for listings area failed: {str(e_area).splitlines()[0]}")

        if listings_area_html:
            print(f"\n--- HTML Snippet of Listings Area (using selector: {listings_area_selector_used}) ---")
            # Print a large portion of this container's HTML
            soup_area = BeautifulSoup(listings_area_html, 'html.parser')
            print(soup_area.prettify()[:30000]) # Print up to 30k chars of the container's content
            print("--- End of Listings Area Snippet ---\n")
            
            # Now, try to find the first listing item *within* this container
            print("Attempting to find the first listing item *within* the identified listings area...")
            soup_for_item_search = BeautifulSoup(listings_area_html, 'html.parser')
            # Selectors for items, relative to the container
            possible_listing_item_selectors_relative = [
                "article[class*='teaserUnified']", "article[class*='listing-item']", 
                "div[class*='teaserUnified']", "div[class*='listing-item']", 
                "div[data-listing-id]", "div[data-testid='listing-item']"
            ]
            first_item_html_within_area = None
            for item_selector_rel in possible_listing_item_selectors_relative:
                first_item = soup_for_item_search.select_one(item_selector_rel)
                if first_item:
                    print(f"Found first listing item within area using relative selector: {item_selector_rel}")
                    first_item_html_within_area = first_item.prettify()
                    break
            
            if first_item_html_within_area:
                print("\n--- HTML Snippet of First Listing Item (found within area) ---")
                print(first_item_html_within_area)
                print("--- End of First Listing Item Snippet ---\n")
            else:
                print("Could not find a distinct listing item within the identified listings area using common sub-selectors.")

        else:
            print("\nCOULD NOT FIND A GENERAL LISTINGS AREA CONTAINER with tried selectors.")
            print("This means the page structure is not as expected, or content is not loading.")
            print("Printing a very large chunk of the current full page source for general inspection (up to 250k chars).")
            print("\n--- General Page Source Snippet (After All Actions) ---\n")
            current_page_source = driver.page_source
            print(f"(Page source length: {len(current_page_source)} chars)")
            print(current_page_source[:250000]) # Increased snippet size
            print("\n--- End of General Page Source Snippet ---\n")
            
        print("Inspection step complete. Returning empty list for this run.")

    except Exception as e:
        print(f"An error occurred during Selenium operation: {e}")
    finally:
        print("Closing WebDriver.")
        driver.quit()
    
    return listings_data

if __name__ == "__main__":
    BASE_GRATKA_URL = "https://gratka.pl/nieruchomosci/mieszkania"
    CITY = "katowice"

    print("Starting Selenium scraper for Gratka.pl...")
    scraped_data = scrape_gratka_listings_selenium(BASE_GRATKA_URL, CITY)

    if scraped_data:
        print(f"\nSuccessfully scraped {len(scraped_data)} listings (sample):")
        for i, listing in enumerate(scraped_data[:3]):
            print(f"\nListing {i+1}:")
            for key, value in listing.items():
                print(f"  {key.capitalize()}: {value}")
    else:
        print("\nNo listings were scraped in this inspection run.")

    print("\nScript finished.")
