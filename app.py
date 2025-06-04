from flask import Flask, render_template, request
import traceback

# Attempt to import from local modules
try:
    from scraper_otodom import scrape_otodom_listings
    print("Successfully imported 'scrape_otodom_listings' from 'scraper_otodom'.")
except ImportError:
    print("Error: Failed to import 'scrape_otodom_listings' from 'scraper_otodom.py'. Ensure the file exists and is in the Python path.")
    scrape_otodom_listings = None

try:
    from filter import filter_apartments
    print("Successfully imported 'filter_apartments' from 'filter'.")
except ImportError:
    print("Error: Failed to import 'filter_apartments' from 'filter.py'. Ensure the file exists and is in the Python path.")
    filter_apartments = None

# report_generator might not be directly used in this route if results.html handles display
# but importing it ensures it's available for future features like "download report".
try:
    from report_generator import generate_html_report
    print("Successfully imported 'generate_html_report' from 'report_generator'.")
except ImportError:
    print("Error: Failed to import 'generate_html_report' from 'report_generator.py'.")
    generate_html_report = None


# Create an instance of the Flask application
app = Flask(__name__)

# --- Configuration Parameters for Web App ---
OTODOM_URL_WEB = "https://www.otodom.pl/pl/oferty/wynajem/mieszkanie/katowice"
MAX_SCRAPING_PAGES_WEB = 1  # Keep low for web responsiveness
LISTINGS_TO_GET_DETAILS_FOR_WEB = 0 # No individual page scraping for the web view for speed
CITY_FILTER_WEB = 'Katowice'


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handles both GET requests (displaying the form) and POST requests
    (processing form submission and displaying results).
    """
    if request.method == 'POST':
        apartments_result = []
        error_message = None
        try:
            min_rooms_str = request.form.get('min_rooms', default='1')
            try:
                min_rooms = int(min_rooms_str)
                if min_rooms < 1: min_rooms = 1 # Ensure min_rooms is at least 1
            except ValueError:
                min_rooms = 1 # Default if conversion fails
                error_message = "Invalid value for minimum rooms, defaulting to 1."


            print(f"Form submitted. Criteria: min_rooms={min_rooms}, city='{CITY_FILTER_WEB}'")

            # --- 1. Scraping Data ---
            raw_listings = []
            if scrape_otodom_listings:
                print(f"Step 1: Scraping data from Otodom (up to {MAX_SCRAPING_PAGES_WEB} page(s), {LISTINGS_TO_GET_DETAILS_FOR_WEB} details)...")
                raw_listings = scrape_otodom_listings(
                    OTODOM_URL_WEB,
                    max_pages_to_scrape=MAX_SCRAPING_PAGES_WEB,
                    listings_to_get_details_for=LISTINGS_TO_GET_DETAILS_FOR_WEB
                )
                if not raw_listings: # Covers both None and empty list
                    print("Scraping returned no listings.")
                    if not error_message: error_message = "No listings found from the source. The website structure might have changed or there are no listings matching the base URL."
                    raw_listings = [] # Ensure it's an empty list for filtering
                else:
                    print(f"Scraped {len(raw_listings)} raw listings.")
            else:
                error_message = "Scraping function is not available due to an import error."
                print(error_message)
                raw_listings = []


            # --- 2. Filtering Data ---
            filtered_listings = []
            if filter_apartments:
                if raw_listings: # Only filter if we have something to filter
                    print(f"Step 2: Filtering listings with criteria: min_rooms={min_rooms}, city='{CITY_FILTER_WEB}'...")
                    filtering_criteria = {'min_rooms': min_rooms, 'city': CITY_FILTER_WEB}
                    filtered_listings = filter_apartments(raw_listings, filtering_criteria)
                    print(f"Found {len(filtered_listings)} listings after filtering.")
                elif not error_message: # If scraping was okay but found nothing, this message is more appropriate
                     error_message = "No listings found from the source that could be filtered."
                apartments_result = filtered_listings
            else:
                if not error_message: error_message = "Filtering function is not available due to an import error."
                print(error_message)
                apartments_result = [] # Cannot filter, so result is empty or raw if we choose

        except Exception as e:
            print(f"An error occurred during POST request processing: {e}")
            print(traceback.format_exc())
            if not error_message: error_message = f"An unexpected error occurred: {e}"
            apartments_result = [] # Ensure empty list on error

        # --- 3. Render Results ---
        return render_template('results.html', apartments=apartments_result, error=error_message)

    # For GET request
    return render_template('index.html')

if __name__ == '__main__':
    """
    Runs the Flask development server.
    """
    # To run this Flask app:
    # 1. Ensure Flask and other dependencies are installed: pip install Flask selenium webdriver_manager beautifulsoup4
    # 2. Ensure scraper_otodom.py, filter.py, report_generator.py are in the same directory or Python path.
    # 3. Ensure templates/index.html and templates/results.html exist.
    # 4. Execute this script: python app.py
    # 5. Open your web browser and go to http://127.0.0.1:5000/

    # Check if all critical functions are imported before running
    if not all([scrape_otodom_listings, filter_apartments]):
        print("\nOne or more critical modules (scraper, filter) failed to import. Flask app will not run effectively.")
        print("Please check the error messages above and ensure all .py files are present and correct.")
    else:
        app.run(debug=True)
