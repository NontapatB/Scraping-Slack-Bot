from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from database import connect_to_database, profile_uris_collection, categories_collection, populars_collection
from scrapping.scrapping_web import scrapping_facebook,scrapping_akexocrist,scrapping_blognone,scrapping_techtalkthai, scrapping_default
from scrapping.scrapping_additional import normalize_uri, get_popular_blog_from_profile, check_medium_category
from pathlib import Path
from dotenv import load_dotenv
from slack_modules.slack_send_message import send_slack_message
import os

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve MongoDB URI, database name, and Slack token from environment variables
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']
SLACK_TOKEN = os.environ['SLACK_TOKEN']

# Connect to the MongoDB database
db = connect_to_database(MONGO_URI, DB_NAME)



# Function to search for and send messages
def search_and_send():
    # Search and send messages for profile URLs
    profile_urls = profile_uris_collection(db)
    for document in profile_urls.find():
        profile_url = document['profile_url']
        channel_id = document['channel_id']
        website = document['website']
        # Normalize profile URL
        normalize_profile_url = normalize_uri(profile_url, 'profile')
        # Get the latest item and its link
        latest_item, new_latest_link_url = scrapping_default(normalize_profile_url)
        if latest_item and new_latest_link_url:
            if new_latest_link_url != document['latest_blog_link']:
                # Update the latest blog link
                profile_urls.update_one({'profile_url': profile_url, 
                                         'channel_id': channel_id},
                                         {'$set': {'latest_blog_link': new_latest_link_url}})

                if document['latest_blog_link'] != new_latest_link_url:
                    # Send a Slack message if there's a new latest blog
                    send_slack_message(channel_id, f"*Latest blog:* {latest_item['title']}\n*Link:* {new_latest_link_url}\n*You can see all profile urls by using command* _*/all_profiles*_")
            else:
               
                print(f"No update in blog: {profile_url}")
                
    # Search and send messages for categories
    categories = categories_collection(db)
    for document in categories.find():
        category = document['category_url']
        channel_id = document['channel_id']
        website = document['website']
        # Normalize category URL
        normalize_category_url = normalize_uri(category, f'category_{website}')
        # Scrapping based on website
        if website == 'facebook':
            latest_item, new_latest_link_url = scrapping_facebook(normalize_category_url)
        elif website == 'akexorcist':
            latest_item, new_latest_link_url = scrapping_akexocrist(normalize_category_url)
        elif website == 'techtalkthai':
            latest_item, new_latest_link_url = scrapping_techtalkthai(normalize_category_url)
        elif website == 'blognone':
            latest_item, new_latest_link_url = scrapping_blognone(normalize_category_url)
        else:
            latest_item, new_latest_link_url = scrapping_default(normalize_category_url)
        # Check for Medium category verification
        if website == 'medium' and check_medium_category(new_latest_link_url):
            print(check_medium_category(new_latest_link_url))
            response_text = f'Latest category not verified'
            return response_text
        if latest_item is not None:
            if new_latest_link_url != document['latest_blog_link'] and website == document['website']:
                # Update the latest blog link        
                categories.update_one({'category_url': category, 
                                    'channel_id': channel_id, 
                                    'website': website}, 
                                    {'$set': {'latest_blog_link': new_latest_link_url}})
                
                
                if document['latest_blog_link'] != new_latest_link_url and document['website'] == website:
                    # Send a Slack message if there's a new latest blog
                    send_slack_message(channel_id, f"*Latest blog in category* {category}:\n*Title:* {latest_item['title']}\n*Link:* {new_latest_link_url}\n*You can see all categories by using command* _*/all_categories*_")
                    # Update the latest blog link
                    categories.update_one({'category_url': category, 
                                        'channel_id': channel_id, 
                                        'website': website}, 
                                        {'$set': {'latest_blog_link': new_latest_link_url}})
            else:
                print(f"No update in category: {category}")

    # Search and update popular blogs
    popular = populars_collection(db)
    for document in profile_urls.find():
        profile_url = document['profile_url']
        normalize_profile_url = normalize_uri(profile_url, 'profile')
        # Get the popular blog from the profile URL
        popular_blog = get_popular_blog_from_profile(normalize_profile_url)
        existing_data = popular.find_one({"profile_url": profile_url})
        if existing_data:
            if popular_blog != existing_data['popular_blog']:
                # Update the popular blog
                popular.update_one(
                    {"profile_url": profile_url},
                    {"$set": {"popular_blog": popular_blog}}
                )
                print(f"Updated collection popular successfully: {profile_url}")
            else:
                print('No popular blog update')
        

