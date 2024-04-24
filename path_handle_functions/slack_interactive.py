from flask import request, json, jsonify
from threading import Thread
from path_handle_functions.interactive_processes.add_process import add_category, add_profile_urls
from path_handle_functions.interactive_processes.button_interactive_process import slack_bookmark_interactive, slack_delete_interactive, slack_popular_interactive, slack_preview_interactive, slack_share_bookmark_interactive, slack_status_bookmark_interactive
from database import connect_to_database, website_categories_collection, bookmarks_collection
from modal.add_form_modal import open_add_category_modal, open_add_profile_modal
from pathlib import Path
from dotenv import load_dotenv
import os
from path_handle_functions.slack_cm_bookmarks import handle_bookmarks

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve MongoDB URI and database name from environment variables
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']

# Connect to MongoDB and initialize collections
db = connect_to_database(MONGO_URI, DB_NAME)
website_collection = website_categories_collection(db)
bookmark_collection = bookmarks_collection(db)

# Function to handle view submission events
# แก้ payload ของ fucntion นี้ด้วย
def handle_type_view_submission(payload):
    # Convert payload to dictionary
    payload = request.form.to_dict()
    print('test payload dict action', payload)
    payload_dict = json.loads(payload['payload'])
    
    action_id = payload_dict['view']['blocks'][0]['element']['action_id']

    if action_id == 'plain_text_input-action_profile':
        # Extract metadata from the payload
        private_metadata = payload_dict['view']['private_metadata']
        channel_id, website = private_metadata.split('___')
        # Extract profile URL input from the payload
        profile_url_input = payload_dict['view']['state']['values']['input_profile']['plain_text_input-action_profile']['value']
        # Split input by comma if multiple URLs provided
        if ',' in profile_url_input:
            profile_urls = str(profile_url_input).split(',')
            print(profile_urls)
        else:
            profile_urls = [profile_url_input]
        # Iterate over profile URLs and start a thread for each URL
        for url_count in range(len(profile_urls)):
            user_name = payload_dict['user']['username']
            user_id = payload_dict['user']['id']
            thread = Thread(target=add_profile_urls, args=(profile_urls[url_count], website, channel_id, user_name, user_id))
            thread.start()
        return jsonify({})
    
    elif action_id == 'plain_text_input-action_category':
        # Extract metadata from the payload
        private_metadata = payload_dict['view']['private_metadata']
        channel_id, website = private_metadata.split('___')
        # Extract category input from the payload
        category_input = payload_dict['view']['state']['values']['input_category']['plain_text_input-action_category']['value']
        # Split input by comma if multiple categories provided
        if ',' in category_input:
            categories = str(category_input).split(',')
        else:
            categories = [category_input]
        # If 'All' selected, retrieve all categories from database
        if 'All' in category_input or 'all' in category_input:
            categories = website_collection.find_one({'website': website}).get('categories', [])
        # Iterate over categories and start a thread for each category
        for url_count in range(len(categories)):
            user_name = payload_dict['user']['username']
            user_id = payload_dict['user']['id']
            thread = Thread(target=add_category, args=(categories[url_count],website, channel_id, user_name, user_id))
            thread.start()
        return jsonify({})
    elif action_id == 'multi_static_select-action':
        # Extract selected categories from the payload
        categories = []
        selected_options = payload_dict['view']['state']['values']['select_category']['multi_static_select-action']['selected_options']
        for option in selected_options:
            value = option['value']
            categories.append(value)
        # Extract metadata from the payload
        private_metadata = payload_dict['view']['private_metadata']
        channel_id, website = private_metadata.split('___')
        # If 'All' selected, retrieve all categories from database
        if 'All' in categories or 'all' in categories:
            categories = website_collection.find_one({'website': website}).get('categories', [])
        # Iterate over categories and start a thread for each category
        for url_count in range(len(categories)):
            user_name = payload_dict['user']['username']
            user_id = payload_dict['user']['id']
            thread = Thread(target=add_category, args=(categories[url_count],website, channel_id, user_name, user_id))
            thread.start()
        return jsonify({})
    elif action_id == 'static_select-action_bookmark_status':
        private_metadata = payload_dict['view']['private_metadata']
        user_name, blog_url = private_metadata.split('___')
        print('sdpfpsdfp..  ', payload_dict)
        status = payload_dict['view']['state']['values']['dLHsN']['static_select-action_bookmark_status']['selected_option']['value']
        bookmark_to_update = bookmark_collection.find_one({'user_name': user_name, 'blog_url': blog_url})
        if bookmark_to_update:
            # อัปเดตค่า 'selected_option_value'
            bookmark_collection.update_one({'_id': bookmark_to_update['_id']}, {'$set': {'status': status}})
        return jsonify({})
    else:
        return jsonify({})
    
# Function to handle block actions
def handle_type_block_actions(actions, trigger_id):
    print("actions test", actions)
    for action in actions:
        action_id = action.get('action_id')
        value = action['selected_option']['value']
        if action_id == 'cm_add_profile':
            open_add_profile_modal(trigger_id, value)
            return jsonify({"success": True})
        elif action_id == 'cm_add_category':
            open_add_category_modal(trigger_id, value)
            return jsonify({"success": True})

# Function to handle button actions
def handle_type_button(payload):
    action_name = payload['actions'][0]['name']
    if action_name == 'delete':
        return slack_delete_interactive(payload)
    elif action_name == 'bookmark':
        return slack_bookmark_interactive(payload)
    elif action_name == 'popular':
        return slack_popular_interactive(payload)
    elif action_name == 'preview':
        return slack_preview_interactive(payload)
    elif action_name == 'share':
        return slack_share_bookmark_interactive(payload)
    elif action_name == 'status':
        return slack_status_bookmark_interactive(payload)
    else:
        return jsonify(text="Invalid action")