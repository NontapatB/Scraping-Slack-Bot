from flask import Flask, request, jsonify
from database import website_categories_collection,connect_to_database, profile_uris_collection, categories_collection, bookmarks_collection,populars_collection
from path_handle_functions.slack_cm_add_profile import handle_add_profile
from path_handle_functions.slack_cm_add_category import handle_add_category
from path_handle_functions.slack_cm_all_profiles import handle_all_profiles
from path_handle_functions.slack_cm_all_categories import handle_all_categories
from path_handle_functions.slack_cm_bookmarks import handle_bookmarks
from path_handle_functions.slack_interactive import handle_type_button,handle_type_view_submission, handle_type_block_actions
import json
from flask import request, jsonify
from pathlib import Path
from dotenv import load_dotenv
import os
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from slack_modules.slack_scheduler import search_and_send

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve environment variables
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB database
db = connect_to_database(MONGO_URI, DB_NAME)

# Initialize a background scheduler
scheduler = BackgroundScheduler(daemon=True)

# Initialize collections from the database
profile_collection = profile_uris_collection(db)
category_collection = categories_collection(db)
bookmark_collection = bookmarks_collection(db)
popular_collection = populars_collection(db)
website_collection = website_categories_collection(db)

# Test route for Slack integration
@app.route('/slack', methods=['GET'])
def slack_test():
    return jsonify(status='OK')

# Help command route for Slack integration
@app.route('/slack/help', methods=['POST'])
def slack_help_command():
    responsetext = '*/add_profile* to add a profile url from websites for update the latest blog\n*/all_profiles* to show all profile urls that user added\n*/add_category* to add a category from websites for update the latest blog\n*/all_categories* to show all categories that user added\n*/bookmarks* to show all bookmarks that user added'
    return jsonify(text=responsetext)

# Command route for adding a profile URL
@app.route('/slack/add_profile', methods=['POST'])
def slack_add_profile_command():
    payload = request.form.to_dict()
    message_block_profile = handle_add_profile(payload)
    return jsonify(message_block_profile)

# Command route for adding a category
@app.route('/slack/add_category', methods=['POST'])
def slack_add_category_command():
    payload = request.form.to_dict()
    message_block_category = handle_add_category(payload)
    return jsonify(message_block_category)

# Route for handling interactive components in Slack messages
@app.route('/slack/interactive', methods=['POST'])
def slack_interactive():
    print(request.content_type)
    payload = json.loads(request.form['payload'])
    print('test payload interactive', payload)
    payload_type = payload.get('type')
    actions = payload.get('actions', [])
    trigger_id = payload.get('trigger_id')
    
    if payload_type == 'view_submission':
        return handle_type_view_submission(payload)
    elif payload_type == 'block_actions':
        return handle_type_block_actions(actions, trigger_id)
    else:
        return handle_type_button(payload)
    
# Command route for showing all profiles
@app.route('/slack/all_profiles', methods=['POST'])
def slack_all_profiles_command():
    channel_id = request.form['channel_id']
    input_text = request.form['text']
    return handle_all_profiles(channel_id, input_text)

# Command route for showing all categories
@app.route('/slack/all_categories', methods=['POST'])
def slack_all_categories_command():
    channel_id = request.form['channel_id']
    input_text = request.form['text']
    return handle_all_categories(channel_id, input_text)

# Command route for showing bookmarks
@app.route('/slack/bookmarks', methods=['POST'])
def slack_show_bookmarks_command():
    payload = request.form.to_dict()
    user_name = payload.get('user_name', None)
    channel_id = payload.get('channel_id', None)
    return handle_bookmarks(user_name, channel_id)

# Add the job to the scheduler
scheduler.add_job(search_and_send, 'interval', seconds=86400)

# Start the scheduler
scheduler.start()

# Register the scheduler shutdown function
atexit.register(lambda: scheduler.shutdown())

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)