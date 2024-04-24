from slack_modules.slack_send_message import send_slack_message
from flask import jsonify, Flask
from database import connect_to_database, profile_uris_collection, categories_collection, bookmarks_collection, validate_data_before_insert_bookmark, populars_collection
from bson import ObjectId
from urllib.parse import unquote
import os
from pathlib import Path
from dotenv import load_dotenv
from path_handle_functions.slack_cm_all_categories import handle_all_categories
from path_handle_functions.slack_cm_all_profiles import handle_all_profiles
from modal.bookmark_statuts_modal import open_bookmark_status_modal
from path_handle_functions.slack_cm_bookmarks import handle_bookmarks

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve MongoDB URI and database name from environment variables
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']

# Connect to MongoDB and initialize collections
db = connect_to_database(MONGO_URI, DB_NAME)
profile_collection = profile_uris_collection(db)
category_collection = categories_collection(db)
bookmark_collection = bookmarks_collection(db)
popular_collection = populars_collection(db)

# Function to handle sharing bookmarks in Slack
def slack_share_bookmark_interactive(payload):
    # Extract necessary data from payload
    value = str(payload['actions'][0]['value'])
    data = value.split('___')
    
    # Check if necessary data is present
    if len(data) >= 4:
        user_name = data[0]
        channel_id = data[1]
        title = data[2]
        blog_url = data[3]

        # Create message to send to Slack
        text_to_slack = f'*Username* _{user_name}_ *shared a bookmark* :hugging_face:\n*Title:* _{title}_\n*Url:* {blog_url}'
        response_text = '*Shared Successfully!*'
        send_slack_message(channel_id, text_to_slack)
    else:
        response_text = '*Fail to share a bookmark!*'
        
    return jsonify(text=response_text)

def slack_status_bookmark_interactive(payload):
    print('test payload bookmark status',payload)
    value = str(payload['actions'][0]['value'])
    trigger_id = payload['trigger_id']
    user_name = payload["user"]["name"]
    channel_id = payload["channel"]["id"]
    open_bookmark_status_modal(trigger_id ,value)
    return handle_bookmarks(user_name, channel_id)

# Function to handle previewing shared content in Slack
def slack_preview_interactive(payload):
    # Extract necessary data from payload
    value = str(payload['actions'][0]['value'])
    response_text = f'{value}'
    data = value.split('___')
    collection = data[0]
    url = data[1]
    title = data[2]
    latest_link = data[3]
    pub_date = data[4]
    user_name = data[5]

    # Determine if the preview is for a profile or category
    if collection == 'profile':
        response_text = f'*Added By:* _{user_name}_\n*From url:* {url}\n*Title:* _{title}_\n*Latest Blog:* {latest_link}\n*Published Date:* {pub_date}'
    else:
        response_text = f'*Added By:* _{user_name}_\n*From category:* {url}\n*Title:* _{title}_\n*Latest Blog:* {latest_link}\n*Published Date:* {pub_date}'
    return jsonify(text=response_text)

# Function to handle deleting items in Slack
def slack_delete_interactive(payload):
    print('text payload delete', payload)
    # Extract ObjectID of the item to delete
    object_id_to_delete = payload['actions'][0]['value']
    channel_id = payload['channel']['id']
    print('text object id delete',object_id_to_delete)

    # Check if the item exists and delete it
    if profile_collection.find_one({'_id': ObjectId(object_id_to_delete)}):
        profile_url_to_delete = profile_collection.find_one({'_id': ObjectId(object_id_to_delete)})['profile_url']

        profile_collection.delete_one({'_id': ObjectId(object_id_to_delete)})

        popular_collection.delete_many({'profile_url': profile_url_to_delete})
        response_text = f"*Profile deleted successfully* :slightly_smiling_face:"
        return handle_all_profiles(channel_id, input_text = '')

        
    elif category_collection.find_one({'_id': ObjectId(object_id_to_delete)}):
        category_collection.delete_one({'_id': ObjectId(object_id_to_delete)})
        response_text = f"*Category deleted successfully* :slightly_smiling_face:"
        return handle_all_categories(channel_id, input_text = '')
        
    elif bookmark_collection.find_one({'_id': ObjectId(object_id_to_delete)}):
        bookmark_collection.delete_one({'_id': ObjectId(object_id_to_delete)})
        response_text = f"*Bookmark deleted successfully* :slightly_smiling_face:"
    else:
        response_text = f"*Object with ObjectId not found in the list*"
    

    return jsonify(text=response_text)

# Function to handle bookmarking content in Slack
def slack_bookmark_interactive(payload):
    # Extract bookmark data from payload
    bookmark_value = unquote(payload['actions'][0]['value'])
    user_name = payload['user']['name']
    print(bookmark_value)
    blog_url = bookmark_value.split('___')[0]
    title = bookmark_value.split('___')[1]
    status = 'Not Read'
    # Check if bookmark already exists in the collection
    existing_bookmark = bookmark_collection.find_one({
        'blog_url': blog_url,
        'user_name': user_name
    })

    if existing_bookmark:
        response_text = "*Bookmark already exists, please check your bookmarks by using /bookmarks command* :face_with_monocle:"

    # Validate and insert bookmark data into the database
    else :
        if validate_data_before_insert_bookmark(blog_url, title, user_name, status):
            bookmark_collection.insert_one({
                'blog_url': blog_url,
                'title': title,
                'user_name': user_name,
                'status': status
            })

            response_text = f"*Link bookmarked successfully:* _{title}_ :heart_eyes:"
        else:
            response_text = f"Invalid data."

    return jsonify(text=response_text)

# Function to handle displaying popular content in Slack
def slack_popular_interactive(payload):
    # Extract data from payload
    value = payload['actions'][0]['value']
    link = value.split('___')[0]
    title_type = value.split('___')[1]
    result = popular_collection.find_one({'profile_url': link})

    # Determine type of content and respond accordingly
    if title_type == 'profile':
        if result :
            popular_blog = result.get('popular_blog')
            response_text = f'*The most popular blog* :star-struck:\n*From:* _{link}_\n*Url Blog:* _{popular_blog}_'
            return jsonify(text=response_text)
        else:
            return jsonify(text='Sorry please try again in a second we are *processing...* :smiling_face_with_tear:')
    else:
        return jsonify(text='error')
