import json # For potential pretty printing during debugging, not strictly required for final output
import traceback # For more detailed error messages

# Attempt to import from local modules
try:
    from scraper_otodom import scrape_otodom_listings
    print("Successfully imported 'scrape_otodom_listings' from 'scraper_otodom'.")
except ImportError:
    print("Error: Failed to import 'scrape_otodom_listings' from 'scraper_otodom.py'. Ensure the file exists and is in the Python path.")
    scrape_otodom_listings = None # Placeholder to allow script to be parsed

try:
    from filter import filter_apartments
    print("Successfully imported 'filter_apartments' from 'filter'.")
except ImportError:
    print("Error: Failed to import 'filter_apartments' from 'filter.py'. Ensure the file exists and is in the Python path.")
    filter_apartments = None

try:
    from report_generator import generate_html_report
    print("Successfully imported 'generate_html_report' from 'report_generator'.")
except ImportError:
    print("Error: Failed to import 'generate_html_report' from 'report_generator.py'. Ensure the file exists and is in the Python path.")
    generate_html_report = None

# --- Configuration Parameters ---
OTODOM_URL = "https://www.otodom.pl/pl/oferty/wynajem/mieszkanie/katowice"
MAX_SCRAPING_PAGES = 2  # As per requirement
# For `listings_to_get_details_for` in scraper_otodom, we'll use its default or adjust if necessary.
# The scraper_otodom.py was last set to fetch details for first 3 listings on page 1.
# And max_pages_to_scrape was set to 1 in its main block for testing detail extraction.
# For this main.py, we'll use MAX_SCRAPING_PAGES for the scraper.
LISTINGS_TO_GET_DETAILS_FOR = 2 # Let's get details for 2 listings to keep it faster for main.py run

FILTERING_CRITERIA = {'min_rooms': 3, 'city': 'Katowice'}
REPORT_FILENAME = "filtered_apartments_report.html"

def main_orchestrator():
    """
    Orchestrates the apartment scraping, filtering, and report generation process.
    """
    print("Starting the apartment aggregation process...")

    # --- 1. Scraping Data ---
    raw_listings = []
    if scrape_otodom_listings:
        try:
            print(f"\nStep 1: Scraping data from Otodom (up to {MAX_SCRAPING_PAGES} pages)...")
            # Pass LISTINGS_TO_GET_DETAILS_FOR to the scraper if its signature supports it.
            # Assuming scrape_otodom_listings takes (url, max_pages, listings_to_get_details_for)
            # Based on previous definition of scrape_otodom_listings:
            raw_listings = scrape_otodom_listings(OTODOM_URL,
                                                 max_pages_to_scrape=MAX_SCRAPING_PAGES,
                                                 listings_to_get_details_for=LISTINGS_TO_GET_DETAILS_FOR)

            if raw_listings:
                print(f"Successfully scraped {len(raw_listings)} raw listings.")
                # Optionally print a sample for debugging
                # print("Sample raw listings:")
                # for i, listing in enumerate(raw_listings[:1]):
                #     print(json.dumps(listing, indent=2, ensure_ascii=False))
            elif raw_listings == []: # Scraper ran but found nothing
                 print("Scraping completed, but no listings were found with the current scraper setup.")
            else: # Scraper might have returned None due to an internal error not caught
                print("Scraping failed or returned no data (returned None).")
                # raw_listings will be an empty list in this case to prevent downstream errors
                raw_listings = []


        except Exception as e:
            print(f"An error occurred during scraping: {e}")
            print("Traceback:")
            traceback.print_exc()
            raw_listings = [] # Ensure it's an empty list on failure
    else:
        print("Scraping function not available due to import error. Skipping scraping.")
        return # Cannot proceed without scraper

    # --- 2. Filtering Data ---
    filtered_listings = []
    if raw_listings and filter_apartments:
        try:
            print(f"\nStep 2: Filtering listings with criteria: {FILTERING_CRITERIA}...")
            filtered_listings = filter_apartments(raw_listings, FILTERING_CRITERIA)
            print(f"Found {len(filtered_listings)} listings after filtering.")
        except Exception as e:
            print(f"An error occurred during filtering: {e}")
            print("Traceback:")
            traceback.print_exc()
            # Continue with potentially empty filtered_listings to generate a report if possible
    elif not raw_listings:
        print("Skipping filtering as no raw listings were obtained.")
    else: # filter_apartments is None
        print("Filtering function not available due to import error. Skipping filtering.")
        filtered_listings = raw_listings # Pass raw listings to report if filter is broken

    # --- 3. Generating Report ---
    if generate_html_report:
        try:
            print(f"\nStep 3: Generating HTML report...")
            if filtered_listings:
                generate_html_report(filtered_listings, output_filepath=REPORT_FILENAME)
                print(f"HTML report '{REPORT_FILENAME}' generated successfully.")
            else:
                print("No listings to report after filtering (or scraping failed). Generating an empty report.")
                generate_html_report([], output_filepath=REPORT_FILENAME) # Generate report with "no data" message
                print(f"Empty HTML report '{REPORT_FILENAME}' generated.")
        except Exception as e:
            print(f"An error occurred during report generation: {e}")
            print("Traceback:")
            traceback.print_exc()
    else:
        print("Report generation function not available due to import error. Skipping report generation.")

    print("\nApartment aggregation process finished.")

if __name__ == "__main__":
    # Ensure all module functions are available before running
    if not all([scrape_otodom_listings, filter_apartments, generate_html_report]):
        print("\nOne or more modules/functions failed to import. Please check the error messages above.")
        print("Aborting main_orchestrator execution.")
    else:
        main_orchestrator()
