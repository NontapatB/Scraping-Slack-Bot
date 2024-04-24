from flask import Flask
from pathlib import Path
from dotenv import load_dotenv
import os
from database import connect_to_database, categories_collection
from flask import request, jsonify

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve MongoDB URI and database name from environment variables
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']

# Connect to MongoDB and initialize categories collection
db = connect_to_database(MONGO_URI, DB_NAME)
category_collection = categories_collection(db)

# Initialize Flask app
app = Flask(__name__)

# Function to handle displaying all categories
def handle_all_categories(channel_id, input_text):
    # Use app_context for testing
    with app.app_context():

        # Retrieve category URLs for the channel from the database
        category_urls = categories_collection(db).find({'channel_id': channel_id})

        attachments = []
        if not input_text:
            # Check if there are categories available for the channel
            if category_collection.find_one({'channel_id' : channel_id}):
                # Iterate over category URLs and prepare attachments for each
                for category in category_urls:
                    latest_link = category.get('latest_blog_link', 
                                            'No latest link available')
                    title = category.get('title', 
                                        'No title availiable')
                    pub_date = category.get('pub_date',
                                            'No published date availiable')
                    attachments.append({
                        "text": f"*From category:* {category['category_url']} \n*Latest update blog:* <{latest_link}| {category['title']}>",
                        "fallback": "Manage",
                        "callback_id": "manage_button",
                        "color": "#3BF7EC",
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
                                "name": "delete",
                                "text": "Delete",
                                "type": "button",
                                "value": str(category['_id']),
                                "style": "danger"
                            },
                            {
                                "name": "preview",
                                "text": "Details>",
                                "type": "button",
                                "value": f"category___{category['category_url']}___{category['title']}___{latest_link}___{pub_date}___{category['user_name']}",
                                "style": "default"
                            }
                        ]
                    })

                # Prepare response containing all categories
                response = {
                    "text": "*All Categories* :books:",
                    "attachments": attachments
                }

                return jsonify(response), 200, {'Content-Type': 'application/json'}
            else:
                # If no categories are found, notify the user
                response = {
                    "text": "*No url founded*, You can add your *profile url* or *category* that you want by using command */add_profile or /add_category* :confused::",
                    "attachments": attachments
                }
                return jsonify(response), 200, {'Content-Type': 'application/json'}
        else:
            # If input text is provided, notify the user to only use /add_profile or /add_category command
            return jsonify(text="Please *only type /add_profile or /add_category* command on message channel. :pleading_face:")