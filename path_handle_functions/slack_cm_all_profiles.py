from pathlib import Path
from dotenv import load_dotenv
import os
from database import connect_to_database, profile_uris_collection
from flask import request, jsonify

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve MongoDB URI and database name from environment variables
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']

# Connect to MongoDB and initialize profile collection
db = connect_to_database(MONGO_URI, DB_NAME)
profile_collection = profile_uris_collection(db)

# Function to handle displaying all profiles
def handle_all_profiles(channel_id, input_text):
    # Extract channel ID and input text from request

    # Retrieve profile URLs for the channel from the database
    profile_urls = profile_uris_collection(db).find({'channel_id': channel_id})

    attachments = []
    if not input_text:
        # Check if there are profiles available for the channel
        if profile_collection.find_one({'channel_id' : channel_id}):
            # Iterate over profile URLs and prepare attachments for each
            for profile in profile_urls:
                latest_link= profile.get('latest_blog_link', 
                                         'No latest link available')
                title = profile.get('title', 
                                    'No title availiable')
                pub_date = profile.get('pub_date', 
                                       'No published date availiable')

                attachments.append({
                    "text": f"*From:* {profile['profile_url']} \n*Latest update blog:* <{latest_link}| {profile['title']}>",
                    "fallback": "Manage",
                    "callback_id": "manage_button",
                    "color": "#F2F",
                    "attachment_type": "default",
                    "actions": [
                        {
                            "name": "bookmark",
                            "text": "Bookmark",
                            "type": "button",
                            "value": f'{latest_link}___{title}',
                            "style": "primary"
                        },
                        {
                            "name": "popular",
                            "text": "Popular",
                            "type": "button",
                            "value": f"{profile['profile_url']}___profile",
                        },
                        {
                            "name": "delete",
                            "text": "Delete",
                            "type": "button",
                            "value": str(profile['_id']),
                            "style": "danger"
                        },
                        {
                            "name": "preview",
                            "text": "Details>",
                            "type": "button",
                            "value": f"profile___{profile['profile_url']}___{profile['title']}___{latest_link}___{pub_date}___{profile['user_name']}",
                            "style": "default"
                        }
                    ]
                })
                # Prepare response containing all profiles
                response = {
                "text": "*All Profile URLs* :books:",
                "attachments": attachments
            }

            return jsonify(response), 200, {'Content-Type': 'application/json'}
        else:
            # If no profiles are found, notify the user
            response = {
                "text": "*No url founded*, You can add your *profile url* or *category* that you want by using command */add_profile or /add_category* :confused::",
                "attachments": attachments
            }
            return jsonify(response), 200, {'Content-Type': 'application/json'}
    else:
        # If input text is provided, notify the user to only use /add_profile or /add_category command
        return jsonify(text="Please *only type /add_profile or /add_category* command on message channel. :pleading_face:")