import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen, Request
from scrapping.scrapping_additional import get_items, fetch_html

# Function for default scraping
def scrapping_default(link):
    # Function to scrape data using default method
    items = get_items(link)
    # Sort items by publication date
    sorted_items = sorted(items, key=lambda x: x['pub_date'], reverse=True)

    if sorted_items:
        # Extract the latest item
        latest_item = sorted_items[0]
        return latest_item, latest_item['link']
    else:
        print("No items found in the XML data.")
        return None, None

# Function for scraping Facebook data
def scrapping_facebook(url):
    # Fetch HTML content from the provided URL
    items = {}
    html = fetch_html(url)
    if html is not None:
        soup = BeautifulSoup(html, 'html.parser')

        # Find all <a> tags with class '_6zxa'
        a_tags_with_class_6zxa = soup.find_all('a', class_='_6zxa')
        print('testfasdlfl      ', a_tags_with_class_6zxa)
        
        if a_tags_with_class_6zxa:
            # Get the first <a> tag
            first_a_tag = a_tags_with_class_6zxa[0]
            # Extract href value
            href_value = first_a_tag.get('href')
            latest_url = f'https://developers.facebook.com{href_value}'
            
            content_text = first_a_tag.text
            pub_date = ''

            items['title'] = content_text
            items['link'] = latest_url
            items['pub_date'] = pub_date

            return items, items['link']
        else:
            return None, None

# Function for scraping from akexocrist website
def scrapping_akexocrist(url):
    # Send a GET request to the provided URL
    response = requests.get(url)
    xml_data = response.text

    soup = BeautifulSoup(xml_data, 'xml')

    # Find the first 'item' tag
    first_item = soup.find('item')
    title = first_item.find('title').text
    link = first_item.find('link').text
    pub_date_str = first_item.find('pubDate').text

    # Parse publication date
    pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %Z')

    formatted_pub_date = pub_date.strftime('%Y-%m-%d')

    items = {}
    items['title'] = title
    items['link'] = link
    items['pub_date'] = formatted_pub_date

    return items, items['link']

# Function for scraping from TechTalkThai website
def scrapping_techtalkthai(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    req = Request(url, headers=headers)

    try:
        response = urlopen(req)
        xml_data = response.read()

        tree = ET.fromstring(xml_data)

        first_item = tree.find(".//item")
        title = first_item.find("title").text
        link = first_item.find("link").text

        pub_date_str = first_item.find("pubDate").text
        pub_date_obj = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
        formatted_pub_date = pub_date_obj.strftime("%Y-%m-%d")

        items = {}
        items['title'] = title
        items['link'] = link
        items['pub_date'] = formatted_pub_date

        return items, items['link']

    except Exception as e:
        print(f"Error: {e}")

# Function for scraping from Blognone website
def scrapping_blognone(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        all_h2_tags = soup.find_all('h2')

        for h2_tag in all_h2_tags:
            a_tag = h2_tag.find('a')
            
            if a_tag:
                href = a_tag.get('href')
                title = a_tag.get('title')
                print("First Link within h2:", href)

                break
        link = 'https://www.blognone.com'+href
        items = {}
        items['title'] = title
        items['link'] = link
        items['pub_date'] = ''

        return items, items['link']
    else:
        print(f"Failed to retrieve the page. Status Code: {response.status_code}")


    
    
