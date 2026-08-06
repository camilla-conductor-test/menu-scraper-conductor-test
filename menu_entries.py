import sys
import subprocess
from bs4 import BeautifulSoup

def ensure_requests():
    """Ensure the 'requests' package is available.

    If missing, prompt the user to install it via pip. On confirmation,
    attempt installation and exit so the script can be re‑run.
    Returns True if the package is already present.
    """
    try:
        import importlib
        importlib.import_module('requests')
        return True
    except ModuleNotFoundError:
        print("The 'requests' package is required to run this scraper.")
        answer = input("Would you like to install it now? [y/N] ").strip().lower()
        if answer == "y":
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
                print("Successfully installed 'requests'. Please re‑run the script.")
                sys.exit(0)
            except Exception as e:
                print(f"Failed to install 'requests': {e}")
                sys.exit(1)
        else:
            print("Installation declined. Exiting.")
            sys.exit(1)

# Ensure requests is available before importing it for use later.
ensure_requests()
import requests

# main page url
MAIN_URL = "https://nutrition.sa.ucsc.edu/"  

dh_names = ["John R. Lewis & College Nine Dining Hall",
        "Cowell & Stevenson Dining Hall",
        "Crown & Merrill Dining Hall",
        "Porter & Kresge Dining Hall",
        "Rachel Carson & Oakes Dining Hall",
        ]

def fetch_links():
    """Fetch all dining hall menu links from the main page."""
    links = []
    try:
        # yoink the main page
        response = requests.get(MAIN_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # <li> elements with class locations
        for li_tag in soup.find_all("li", class_="locations"):
            a_tag = li_tag.find("a")  # Get the <a> tag inside <li>
            if a_tag and a_tag.get("href"):
                href = a_tag["href"]
                # Build full URL if the link is delulu
                full_url = href if href.startswith("http") else f"{MAIN_URL.rsplit('/', 1)[0]}/{href}"
                if "Hall" in full_url:
                    links.append(full_url)
        return links
    except Exception as e:
        print(f"Error fetching links: {e}")
        return []



def fetch_menu(dh_link):
    """Fetch and parse the menu content from a specific dining hall URL using a session."""
    try:
        #session object
        session = requests.Session()

        # Visit the main menu page to establish session
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        session.get(MAIN_URL, headers=headers)  # Heres main page uwu

        #visit dining hall menu page
        response = session.get(dh_link, headers=headers)
        response.raise_for_status()  # Raise error if the request fails
        soup = BeautifulSoup(response.text, "html.parser")

        
        # Parse the dhhh menu
        menu_data = {}  # Dictionary to store categories and items
        unique_items = set()  # Set to track unique items across all categories


        # Start with the main table containing the menu
        menu_start = soup.find("table", bordercolor="#CCC")
        if not menu_start:
            print("Menu table not found.")
            return {}, set()

        # Delulu through categories and items
        current_category = None
        for element in menu_start.find_all(["div", "tr"]):  # Look for all divs and rows in the table
            # Check for category (shortmenumeals)
            category = element.find("div", class_="shortmenumeals")
            if category:
                current_category = category.get_text(strip=True)
                menu_data[current_category] = []  # Initialize category in the dictionary
                continue

            # Check for food items (shortmenurecipes)
            recipes = element.find_all("div", class_="shortmenurecipes")
            for recipe in recipes:
                item_text = recipe.get_text(strip=True)
                if item_text:
                    # Add to the current category and unique set
                    if current_category and item_text not in menu_data[current_category]:
                        menu_data[current_category].append(item_text)
                    unique_items.add(item_text)

        # Print results (for testing)
        for category, items in menu_data.items():
            print(f"{category}:")
            for item in items:
                print(f"  - {item}")
        print(f"Total unique menu items: {len(unique_items)}")

        return menu_data, unique_items  # Return menu data and unique items
    except Exception as e:
        print(f"Error fetching menu: {e}")
        return {}, set()


def search_food(menu_data, keyword):
    """Search the menu for a specific food keyword and return meal categories."""
    keyword = keyword.lower()
    
    if keyword.endswith("s"):  # If the input is plural
        singular_keyword = keyword[:-1]  # Remove the trailing s
        plural_keyword = keyword  # Keep the plural as is
    else:  # If the input is singular 
        singular_keyword = keyword  # Keep the singular as is
        plural_keyword = f"{keyword}s"  # Add an "s" to make it plural

    results = {}  # To store categories where the keyword is found

    # Search each category for the keyword
    for category, items in menu_data.items():
        for item in items:
            item_lower = item.lower()
            if keyword in item_lower or plural_keyword in item_lower:
                if category not in results:
                    results[category] = []
                results[category].append(item)

    if results:
        return results #results is a dict
    else:
        return None  # No results found

if __name__ == "__main__":

    dhs_with_items = {}

    corresponding_num = 0

    search_keyword = input("What food are you searching for? : ")

    for link in fetch_links():
        print(f"---{dh_names[corresponding_num]}---")
        menu, unique_items = fetch_menu(link)
        found_keyword = search_food(menu, search_keyword)

        if found_keyword:
            dhs_with_items[dh_names[corresponding_num]] = found_keyword
        corresponding_num += 1

    if not dhs_with_items:
        print(f"\nUnfortunately, no dining halls seem to be serving {search_keyword} :(")
    else:
        print("-----------------------------------------------------------------")
        print(f"\nYour desired {search_keyword} is served today, at the following dining halls: ")

        for dh,items in dhs_with_items.items():
            print(f"\n---{dh}---")

            for meal, food_items in items.items():
                print(f"{meal}: ")
                for item in food_items:
                    print(f" - {item}")



