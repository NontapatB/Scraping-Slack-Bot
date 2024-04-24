import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dateutil import parser
from database import connect_to_database,facebook_mapping_categories_collection
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve MongoDB URI and database name from environment variables
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']

# Connect to the MongoDB database
db = connect_to_database(MONGO_URI, DB_NAME)

# Retrieve Facebook mapping categories from the database
website_categories = facebook_mapping_categories_collection(db).find_one({})

# Function to fetch items from an XML feed
def get_items(link):
    try:
        # Send a GET request to the provided link
        response = requests.get(link)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print(f"Failed to fetch data from {link}. Error: {e}")
        return None, None 

    try:
        # Parse XML data
        root = ET.fromstring(response.text)
    except ET.ParseError as e:
        # Handle XML parsing errors
        print(f"Failed to parse XML data. Error: {e}")
        print("Response Text:", response.text)
        return None, None

    items = []

    # Iterate over items in the XML tree
    for item_elem in root.findall('.//item'):
        # Extract title, link, and publication date from each item
        title = item_elem.find('title').text.strip()
        link = item_elem.find('link').text.strip()
        pub_date_str = item_elem.find('pubDate').text.strip()

        try:
            # Parse publication date using dateutil.parser
            pub_date = parser.parse(pub_date_str)
        except ValueError:
            pub_date = parser.parse(pub_date_str + ' UTC')

        # Append extracted data to the items list
        items.append({
            'title': title,
            'link': link,
            'pub_date': pub_date,
        })
    return items

# Function to normalize a URL based on its type
def normalize_uri(url, type):
    if type == 'profile':
        parsed_url = urlparse(url)
        if parsed_url.netloc == 'medium.com':
            if '/@' in parsed_url.path:
                username = parsed_url.path.split('/@')[1]
                normalized_url = f"https://medium.com/feed/@{username}"
            elif parsed_url.path.startswith('/'):
                username = parsed_url.path.split('/')[-1]
                normalized_url = f"https://medium.com/feed/{username}"
            else:
                normalized_url = url
        elif '.medium.com' in parsed_url.netloc:
            username = parsed_url.netloc.split('.')[0]
            normalized_url = f"https://medium.com/feed/@{username}"
        else:
            normalized_url = url
        return normalized_url
    elif type == 'category_somkiat':
        normalized_url = f'https://www.somkiat.cc/category/{url}/feed/'
        return normalized_url
    elif type == 'category_medium':
        normalized_url = f'https://medium.com/feed/tag/{url}'
        return normalized_url
    elif type == 'category_facebook':
        mapping = website_categories.get(str(url).lower(), 'No data found')
        if mapping != 'No data found':
            normalized_url = f'https://developers.facebook.com/community?category={mapping}'
            return normalized_url
        else:
            return None
    elif type == 'category_tamemo':
        return normalized_url
    elif type == 'category_akexorcist':
        normalized_url = f'https://akexorcist.dev/tag/{url}/feed'
        return normalized_url
    elif type == 'category_techtalkthai':
        normalized_url = f'https://www.techtalkthai.com/category/{url}/feed'
        return normalized_url
    elif type == 'category_blognone':
        normalized_url = f'https://www.blognone.com/topics/{url}'
        return normalized_url
    else:
        return url
    
def fetch_html(url):
    try:
        # Fetch HTML content from the provided URL
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print(f"Failed to fetch HTML from {url}. Error: {e}")
        return None
    
def process_url(url):
    print(f"Processing URL: {url}")
    # Fetch HTML content from the URL
    html = fetch_html(url)
    if html is not None:
        soup = BeautifulSoup(html, "lxml")
        # Select all buttons inside div with class 'bl'
        buttons_inside_bl_span = soup.select('div.bl button')

        if buttons_inside_bl_span:
            # Calculate the total numeric count of buttons
            numeric_count = sum(int(button.text.strip()) for button in buttons_inside_bl_span if button.text.strip().isdigit())
            print(f"Total Numeric Count for {url}: {numeric_count}")
            return numeric_count
        else:
            print(f"Not founded <button> inside <div class='bl'> and <span> in URL: {url}")

def check_medium_category(url):
    # Fetch HTML content from the URL
    html = fetch_html(url)
    
    if html is not None:
        soup = BeautifulSoup(html, "html.parser")
        # Select all divs whose class starts with 'c'
        divs_starting_with_c = soup.select('div[class^="c"]')

        for div in divs_starting_with_c:
            # Extract paragraphs content
            paragraphs_content = [p.text.strip() for p in div.find_all('p')]
            combined_content = ' '.join(paragraphs_content)
            if len(combined_content) > 500:
                return False
        
        return True
    
def get_popular_blog_from_profile(link, min_items=1, max_items=10):
    # Fetch items from the provided link
    items = get_items(link)
    # Sort items by publication date
    sorted_items = sorted(items, key=lambda x: x['pub_date'], reverse=True)
    # Determine the number of items to process
    num_items_to_process = min(max(len(sorted_items), min_items), max_items)
    # Process each item and get numeric counts
    numeric_counts = [process_url(item['link']) for item in items[:num_items_to_process]]
    # Get the maximum numeric count
    max_numeric_count = max(numeric_counts, default=0)
    # Get the URL with the maximum numeric count
    url_with_max_numeric_count = items[numeric_counts.index(max_numeric_count)]['link'] if max_numeric_count > 0 else None

    return url_with_max_numeric_count