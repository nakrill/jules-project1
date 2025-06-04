import json

def generate_html_report(filtered_apartments):
    """
    Generates an HTML report string from a list of apartment data.

    Args:
        filtered_apartments (list): A list of dictionaries, where each
                                    dictionary represents an apartment.
    Returns:
        str: The generated HTML content as a string.
    """
    html_content = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apartment Listings Report</title>
    <style>
        body { font-family: sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
        .container { max-width: 900px; margin: auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .apartment { border: 1px solid #ccc; padding: 15px; margin-bottom: 20px; border-radius: 5px; background-color: #fff; }
        .apartment h3 { margin-top: 0; color: #0056b3; }
        .apartment p { margin: 8px 0; line-height: 1.6; }
        .apartment p strong { color: #555; }
        .apartment a { color: #007bff; text-decoration: none; }
        .apartment a:hover { text-decoration: underline; }
        hr { border: 0; height: 1px; background: #ddd; margin: 20px 0; }
        .no-data { text-align: center; color: #777; font-size: 1.2em; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Filtered Apartment Listings</h1>
"""

    if not filtered_apartments:
        html_content += '<p class="no-data">No apartments found matching the criteria.</p>\n'
    else:
        for i, apartment in enumerate(filtered_apartments):
            html_content += '        <div class="apartment">\n'
            html_content += f"            <h3>{apartment.get('title', 'N/A')}</h3>\n"

            price_str = apartment.get('price', 'N/A')
            additional_rent = apartment.get('additional_rent', 'N/A')
            if additional_rent and additional_rent != "N/A" and price_str != "N/A" and "zapytaj" not in price_str.lower() :
                price_str += f" + {additional_rent}"
            elif price_str == "N/A" and additional_rent and additional_rent != "N/A":
                 price_str = additional_rent # Show additional_rent if main price is N/A

            html_content += f"            <p><strong>Price:</strong> {price_str}</p>\n"
            html_content += f"            <p><strong>Location:</strong> {apartment.get('location', 'N/A')}</p>\n"
            html_content += f"            <p><strong>Rooms:</strong> {apartment.get('rooms', 'N/A')}</p>\n"
            html_content += f"            <p><strong>Area:</strong> {apartment.get('area', 'N/A')}</p>\n"

            link = apartment.get('link', '#')
            if link != "#" and link != "N/A":
                 html_content += f'            <p><strong>Link:</strong> <a href="{link}" target="_blank">View Original Listing</a></p>\n'
            else:
                html_content += f'            <p><strong>Link:</strong> N/A</p>\n'

            # Add pet policy and lease term if they exist
            if 'pet_policy_info' in apartment:
                 html_content += f"            <p><strong>Pet Policy:</strong> {apartment.get('pet_policy_info', 'N/A')}</p>\n"
            if 'lease_term_info' in apartment:
                 html_content += f"            <p><strong>Lease Term:</strong> {apartment.get('lease_term_info', 'N/A')}</p>\n"

            html_content += "        </div>\n"
            if i < len(filtered_apartments) - 1:
                html_content += "        <hr>\n"

    html_content += """
    </div>
</body>
</html>
"""
    return html_content


if __name__ == "__main__":
    sample_data = [
        {
            "title": "Mieszkanie w Katowicach Centrum", "price": "2500 zł",
            "additional_rent": "500 zł", "location": "Katowice, Śródmieście",
            "rooms": "3 pokoje", "area": "60 m²", "link": "https://example.com/link1",
            "pet_policy_info": "Akceptowane", "lease_term_info": "Minimum 12 miesięcy"
        },
        {
            "title": "Kawalerka blisko rynku", "price": "1800 zł",
            "additional_rent": "N/A", "location": "Katowice, Rynek",
            "rooms": "Kawalerka", "area": "30 m²", "link": "https://example.com/link2",
            "pet_policy_info": "Nieakceptowane", "lease_term_info": "N/A"
        },
        {
            "title": "Apartament bez linku", "price": "3200 zł",
            "additional_rent": "600 zł", "location": "Kraków, Stare Miasto",
            "rooms": "2 pokoje", "area": "55 m²", "link": "N/A", # Test N/A link
            "pet_policy_info": "Information not found", "lease_term_info": "Minimum 6 miesięcy"
        },
        {
            "title": "Mieszkanie bez ceny", "price": "N/A",
            "additional_rent": "N/A", "location": "Katowice, Koszutka",
            "rooms": "1 pokój", "area": "28 m²", "link": "https://example.com/link5",
            "pet_policy_info": "N/A", "lease_term_info": "N/A"
        }
    ]

    empty_data = []

    # Generate HTML string from sample data
    sample_html_output = generate_html_report(sample_data)
    output_filepath_sample = "apartments_report_from_string_sample.html"
    try:
        with open(output_filepath_sample, 'w', encoding='utf-8') as f:
            f.write(sample_html_output)
        print(f"Sample report generated to: {output_filepath_sample}")
    except IOError as e:
        print(f"Error writing sample HTML report to file: {e}")

    # Generate HTML string from empty data
    empty_html_output = generate_html_report(empty_data)
    output_filepath_empty = "apartments_report_from_string_empty.html"
    try:
        with open(output_filepath_empty, 'w', encoding='utf-8') as f:
            f.write(empty_html_output)
        print(f"Empty report generated to: {output_filepath_empty}")
    except IOError as e:
        print(f"Error writing empty HTML report to file: {e}")

    print("\nScript finished. Check for generated HTML files from string output.")
