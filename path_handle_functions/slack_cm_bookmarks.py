from pathlib import Path
from dotenv import load_dotenv
import os
from database import connect_to_database, bookmarks_collection
from flask import jsonify

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve MongoDB URI and database name from environment variables
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']

# Connect to MongoDB and initialize bookmarks collection
db = connect_to_database(MONGO_URI, DB_NAME)
bookmark_collection = bookmarks_collection(db)

# Function to handle displaying bookmarks for a user
def handle_bookmarks(user_name, channel_id):
    # Extract user name and channel ID from payload
    # user_name = payload.get('user_name', None)
    # channel_id = payload.get('channel_id', None)

    # Retrieve bookmarks for the user from the database
    bookmarks = bookmark_collection.find({'user_name': user_name})

    # Check if there are any bookmarks for the user
    if not bookmark_collection.find_one({'user_name' : user_name}):
        # If no bookmarks are found, prepare response indicating so
        response = {
            "text": f"*No Bookmarks found in user* {user_name} :confused:\nYou can add your bookmarks by using command *_/show_*"
        }
    else:
        # If bookmarks are found, prepare attachments for each bookmark
        attachments = []

        for bookmark in bookmarks:
            attachments.append({
                
                "text": f"*Title:* {bookmark['title']}\n*Url:* {bookmark['blog_url']}\n*Status:* {bookmark['status']}",
                "fallback": "Delete",
                "callback_id": "delete_bookmark_button",
                "color": "#FAFF17",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "delete",
                        "text": "Delete",
                        "type": "button",
                        "value": str(bookmark['_id']),
                        "style": "danger"
                    },
                    {
                        "name": "share",
                        "text": "Share",
                        "type": "button",
                        "value": f"{user_name}___{channel_id}___{bookmark['title']}___{bookmark['blog_url']}",
                        "style": "default"
                    },
                    {
                        "name": "status",
                        "text": "Status",
                        "type": "button",
                        "value": f"{user_name}___{bookmark['blog_url']}",
                        "style": "primary"
                    },
                ]
            })

        # Prepare response containing bookmarks for the user
        response = {
            "text": f"*Bookmarks for user* {user_name} :books:",
            "attachments": attachments
        }

    # Return response as JSON
    return jsonify(response), 200, {'Content-Type': 'application/json'}