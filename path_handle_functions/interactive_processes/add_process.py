from slack_modules.slack_send_message import send_slack_message, send_slack_invisible_message
from flask import jsonify, Flask
from database import connect_to_database, profile_uris_collection, categories_collection, bookmarks_collection, populars_collection
import os
from pathlib import Path
from dotenv import load_dotenv
from scrapping.scrapping_web import scrapping_facebook,scrapping_default, scrapping_akexocrist, scrapping_blognone, scrapping_techtalkthai
from scrapping.scrapping_additional import normalize_uri, get_popular_blog_from_profile, check_medium_category
from database import validate_data_before_insert_url
from threading import Thread

# Load enviroment variables from .env (vaults)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve MongoDB URI and database name from enviroment variables
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME'] 

# Connect to MongoDB and initialize collections
db = connect_to_database(MONGO_URI, DB_NAME)
profile_collection = profile_uris_collection(db)
category_collection = categories_collection(db)
bookmark_collection = bookmarks_collection(db)
popular_collection = populars_collection(db)

# Function to add profile URLs
def add_profile_urls(url,website, channel_id, user_name, user_id):
    # Check if the URL is a Medium profile link
    if 'medium.com/' not in url.lower():
        response_text = "Invalid link. *Only Medium profile links* are allowed :confused:"
    else:
        # Check if the profile URL already exists in the list
        if profile_collection.find_one({'profile_url': url, 'channel_id' : channel_id}):
            response_text = f"*Profile* _{url}_ *already exists in the list* :confused:"
            send_slack_invisible_message(channel_id, user_id  ,response_text)
        # Check if the profile URL is already marked as popular
        elif popular_collection.find_one({'profile_url': url}):
            response_text = f"*Popular* _{url}_ *already exists in the list* :confused:"
            send_slack_invisible_message(channel_id,  user_id ,response_text)
        else:
            # Normalize the profile URL and scrape the latest blog link
            normalize_profile_uri = normalize_uri(url, 'profile')
            latest_item, new_latest_link_url = scrapping_default(normalize_profile_uri)
            # Validate data before inserting into the database
            if validate_data_before_insert_url(url, latest_item['title'], new_latest_link_url, channel_id):
                # Insert profile URL into the database
                profile_collection.insert_one({'profile_url' : url, 
                                                'title': latest_item['title'],
                                                'latest_blog_link': new_latest_link_url, 
                                                'channel_id': channel_id, 
                                                'pub_date': str(latest_item['pub_date']).split(' ')[0],
                                                'user_name': user_name,
                                                'website': website})
                response_text = f'*Link* {url} *added and verified successfully* :partying_face:'
                send_slack_message(channel_id,  response_text)
                # Start a thread to process popular blogs from the profile
                thread = Thread(target=process_popular_blog, args=(url, normalize_profile_uri))
                thread.start()
            else:
                return print("Invalid data.")
    return response_text

# Function to add categories
def add_category(category, website, channel_id, user_name, user_id):
    # Check if category is provided
    if not category:
        return jsonify(text="Please enter the *Category* that you want to add.")
    
    if channel_id:
        # Check if the category URL is valid
        if '.com' in category.lower():
            response_text = "Invalid link. *Only Category* are allowed. :confused:"
        else:
            if category_collection.find_one({'category_url': category.lower(),
                                             'channel_id' : channel_id, 
                                             'website' : website}):
                response_text = f"Category _{category}_ *already exists* in the list :confused:"
                send_slack_invisible_message(channel_id, user_id,  response_text)
            else:
                # Normalize the category URL and scrape the latest blog link
                normalize_category_uri = normalize_uri(category, f'category_{website}')
                if website == 'facebook':
                    latest_item, new_latest_link_url = scrapping_facebook(normalize_category_uri)
                    print("latestfb",latest_item)
                elif website == 'akexorcist':
                    latest_item, new_latest_link_url = scrapping_akexocrist(normalize_category_uri)
                elif website == 'techtalkthai':
                    latest_item, new_latest_link_url = scrapping_techtalkthai(normalize_category_uri)
                elif website == 'blognone':
                    latest_item, new_latest_link_url = scrapping_blognone(normalize_category_uri)
                else:
                    latest_item, new_latest_link_url = scrapping_default(normalize_category_uri)
                # Check if the category blog is not verified
                if website == 'medium' and check_medium_category(new_latest_link_url):
                    print(check_medium_category(new_latest_link_url))
                    response_text = f'*Latest category blog not verified, Please try again later*'
                    send_slack_invisible_message(channel_id,  user_id ,response_text)
                    return response_text
                if latest_item is None:
                    response_text = f"*Oh!*:hushed: *It looks like category* _{category}_ *doesn't exist in* _{website}_ *website* or the blog *doesn't exist in* _{website}_ *website*"
                    send_slack_invisible_message(channel_id, user_id, response_text)
                elif validate_data_before_insert_url(category.lower(),
                                                    latest_item['title'],
                                                    new_latest_link_url, channel_id):
                    # Insert category into the database
                    category_collection.insert_one({'category_url' : category.lower(),
                                                    'title': latest_item['title'], 
                                                    'latest_blog_link': new_latest_link_url, 
                                                    'channel_id': channel_id, 
                                                    'pub_date': str(latest_item['pub_date']).split(' ')[0],
                                                    'user_name': user_name,'website': website})
                    response_text = f'*Category* _{category}_ *added and verified successfully* :partying_face:'
                    send_slack_message(channel_id,  response_text)
                else:
                    response_text = f"*Oh!*:hushed: *It looks like category* _{category}_ *doesn't exist in* _{website}_ *website*"
                    return print("Invalid data.")
        return response_text
    else:
        response_text = f'*Can not find channel ID :* {channel_id} :confused:'
    print('cate response',response_text)
    return response_text

# Function to process popular blogs
def process_popular_blog(profile_url, normalize_profile_uri):
    popular_blog = get_popular_blog_from_profile(normalize_profile_uri)
    if popular_blog:
        popular_collection.insert_one({'profile_url': profile_url, 
                                    'popular_blog': popular_blog})
    else:
        popular_collection.insert_one({'profile_url': profile_url, 
                                    'popular_blog': ''})
