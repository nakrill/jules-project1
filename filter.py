import re
import json

def parse_room_count(room_string):
    """
    Parses a room description string (e.g., "3 pokoje", "kawalerka")
    and returns an integer number of rooms.
    Returns 0 if unparseable or "N/A".
    """
    if not isinstance(room_string, str) or room_string == "N/A":
        return 0

    room_string_lower = room_string.lower()

    if "kawalerka" in room_string_lower:
        return 1

    match = re.search(r'(\d+)', room_string_lower)
    if match:
        return int(match.group(1))

    return 0 # Default for unknown formats

def filter_apartments(apartments_data, criteria):
    """
    Filters a list of apartment data based on specified criteria.

    Args:
        apartments_data (list): A list of dictionaries, where each dictionary
                                represents an apartment.
        criteria (dict): A dictionary specifying filter conditions.
                         Supported criteria: 'min_rooms' (int), 'city' (str).

    Returns:
        list: A new list containing only the apartments that match all
              applied criteria.
    """
    filtered_results = []

    min_rooms_filter = criteria.get('min_rooms')
    city_filter = criteria.get('city')
    if city_filter:
        city_filter = city_filter.lower()

    for apartment in apartments_data:
        passes_all_criteria = True

        # Number of Rooms Filtering
        if min_rooms_filter is not None:
            room_count_str = apartment.get('rooms', "N/A")
            actual_rooms = parse_room_count(room_count_str)
            if actual_rooms == 0 and room_count_str != "N/A": # if parse_room_count returned 0 for something not "N/A"
                print(f"Warning: Could not parse room count for '{room_count_str}', treating as 0 rooms.")

            if actual_rooms < min_rooms_filter:
                passes_all_criteria = False

        # City Filtering
        if passes_all_criteria and city_filter is not None:
            location_str = apartment.get('location', "N/A")
            if not isinstance(location_str, str) or location_str == "N/A":
                passes_all_criteria = False # Does not match if location is N/A and city filter is active
            elif city_filter not in location_str.lower():
                passes_all_criteria = False

        if passes_all_criteria:
            filtered_results.append(apartment)

    return filtered_results

if __name__ == "__main__":
    sample_apartments = [
        {
            "title": "Mieszkanie w Katowicach Centrum",
            "price": "2500 zł", "additional_rent": "500 zł",
            "location": "Katowice, Śródmieście",
            "rooms": "3 pokoje", "area": "60 m²", "link": "url1",
            "pet_policy_info": "Akceptowane", "lease_term_info": "Minimum 12 miesięcy"
        },
        {
            "title": "Kawalerka blisko rynku",
            "price": "1800 zł", "additional_rent": "300 zł",
            "location": "Katowice, Rynek",
            "rooms": "Kawalerka", "area": "30 m²", "link": "url2",
            "pet_policy_info": "N/A", "lease_term_info": "N/A"
        },
        {
            "title": "Duże mieszkanie poza Katowicami",
            "price": "3000 zł", "additional_rent": "N/A",
            "location": "Chorzów, Centrum",
            "rooms": "4 pokoje", "area": "80 m²", "link": "url3",
            "pet_policy_info": "Nieakceptowane", "lease_term_info": "Długoterminowy"
        },
        {
            "title": "Mieszkanie 2-pokojowe Katowice",
            "price": "2200 zł", "additional_rent": "400 zł",
            "location": "Katowice, Ligota",
            "rooms": "2 pokoje", "area": "45 m²", "link": "url4",
            "pet_policy_info": "Akceptowane", "lease_term_info": "Minimum rok"
        },
        {
            "title": "Studio w Katowicach",
            "price": "1600 zł", "additional_rent": "250 zł",
            "location": "Katowice, Koszutka",
            "rooms": "1 pokój", "area": "28 m²", "link": "url5", # Equivalent to Kawalerka
            "pet_policy_info": "N/A", "lease_term_info": "N/A"
        },
         {
            "title": "Mieszkanie bez informacji o pokojach",
            "price": "2000 zł", "additional_rent": "N/A",
            "location": "Katowice, Dąb",
            "rooms": "N/A", "area": "50 m²", "link": "url6",
            "pet_policy_info": "N/A", "lease_term_info": "N/A"
        },
        {
            "title": "Mieszkanie w Sosnowcu",
            "price": "1900 zł", "additional_rent": "350 zł",
            "location": "Sosnowiec",
            "rooms": "2 pokoje", "area": "48 m²", "link": "url7",
            "pet_policy_info": "N/A", "lease_term_info": "N/A"
        },
        {
            "title": "Luksusowy apartament Katowice",
            "price": "4500 zł", "additional_rent": "N/A",
            "location": "Katowice, Brynów",
            "rooms": "4 Pokoje", # Test case-insensitivity and space
            "area": "100 m²", "link": "url8",
            "pet_policy_info": "N/A", "lease_term_info": "N/A"
        }
    ]

    print("Original Apartments:")
    for apt in sample_apartments:
        print(json.dumps(apt, indent=2, ensure_ascii=False))

    criteria1 = {'min_rooms': 3, 'city': 'Katowice'}
    print(f"\nFiltering with criteria: {criteria1}")
    filtered_apartments1 = filter_apartments(sample_apartments, criteria1)
    print(f"Found {len(filtered_apartments1)} apartments matching criteria1:")
    for apt in filtered_apartments1:
        print(json.dumps(apt, indent=2, ensure_ascii=False))

    criteria2 = {'min_rooms': 1, 'city': 'Katowice'}
    print(f"\nFiltering with criteria: {criteria2}")
    filtered_apartments2 = filter_apartments(sample_apartments, criteria2)
    print(f"Found {len(filtered_apartments2)} apartments matching criteria2:")
    for apt in filtered_apartments2:
        print(json.dumps(apt, indent=2, ensure_ascii=False))

    criteria3 = {'city': 'Sosnowiec'}
    print(f"\nFiltering with criteria: {criteria3}")
    filtered_apartments3 = filter_apartments(sample_apartments, criteria3)
    print(f"Found {len(filtered_apartments3)} apartments matching criteria3:")
    for apt in filtered_apartments3:
        print(json.dumps(apt, indent=2, ensure_ascii=False))

    criteria4 = {'min_rooms': 4} # No city specified
    print(f"\nFiltering with criteria: {criteria4}")
    filtered_apartments4 = filter_apartments(sample_apartments, criteria4)
    print(f"Found {len(filtered_apartments4)} apartments matching criteria4:")
    for apt in filtered_apartments4:
        print(json.dumps(apt, indent=2, ensure_ascii=False))

    print("\nScript finished.")
