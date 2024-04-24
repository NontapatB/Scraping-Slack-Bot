import requests
from pathlib import Path
from dotenv import load_dotenv
import os

from database import connect_to_database, website_categories_collection

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve environment variables
SLACK_TOKEN = os.environ['SLACK_TOKEN']
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']

# Connect to the MongoDB database
db = connect_to_database(MONGO_URI, DB_NAME)

# Access the website categories collection in the database
website_collection = website_categories_collection(db)

# Function to open a modal for adding profile URLs
def open_add_profile_modal(trigger_id,value):
    # Extract channel ID and website from the provided value
    website = str(value).split('___')[1]
    channel_id = str(value).split('___')[0]
    
    try:
        # Define the data for the modal view
        modal_data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "title": {
                    "type": "plain_text",
                    "text": "Add Profile Url Form",
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Submit",
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel",
                },
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "input_profile",
                        "element": {
                            "type": "plain_text_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Enter Profile URL/Profile URLs here",
                            },
                            "action_id": "plain_text_input-action_profile"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Enter Profile URL/Profile Urls from medium",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "plain_text",
                                "text": "*You can add multiple urls by follow this example > ex. url1,url2,url3",
                            }
                        ]
                    }
                ],
                "private_metadata": f'{channel_id}___{website}',
            }
        }

        # Make a request to open the modal view
        slack_api_url = 'https://slack.com/api/views.open'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SLACK_TOKEN}'
        }
        response = requests.post(slack_api_url, json=modal_data, headers=headers)

        if response.status_code == 200:
            print("Modal Slack API call successful")
        else:
            print("Modal Slack API call failed:", response.text)
    except Exception as e:
        print("Error opening modal:", e)

# Function to open a modal for adding categories
def open_add_category_modal(trigger_id, value):
    # Extract channel ID and website from the provided value
    website = str(value).split('___')[1]
    channel_id = str(value).split('___')[0]

    # Define blocks for the modal view based on the website
    if website != 'medium' and website != 'blognone':
        categories = website_collection.find_one({'website': website})
        category_options = []

        if categories:
            for category in categories['categories']:
                category_options.append({
                    "text": {
                        "type": "plain_text",
                        "text": category,
                    },
                    "value": f"{category}"
                })
            print('category option', category_options)
        else:
            print("No categories found for the specified website.")

        block_category_text ={
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": f"*You can select All to add all categories from website {website}",
                    }
                ]
            }
        block_category = [
            {
                "type": "input",
                "block_id": "select_category",
                "element": {
                    "type": "multi_static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a category/categories",
                    },
                    "options": category_options,
                    "action_id": "multi_static_select-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": f"Select category from website {website} here",
                },
            },
            block_category_text,
        ]
        print('test block_category', block_category)
    else:
        block_category_text ={
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "*You can add multiple categories by following this example > ex. ctg1,ctg2,ctg3",
                    }
                ]
            }
        block_category = [
                {
                        "type": "input",
                        "block_id": "input_category",
                        "element": {
                            "type": "plain_text_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Enter a category/categories",
                            },
                            "action_id": "plain_text_input-action_category"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": f"Enter category from {website} here",
                        },
                },
                block_category_text,
            ]

    try:
        modal_data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "title": {
                    "type": "plain_text",
                    "text": "Add Category Form",
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Submit",
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel",
                },
                "blocks": block_category,
                "private_metadata": f'{channel_id}___{website}',
            },
            
        }

        slack_api_url = 'https://slack.com/api/views.open'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SLACK_TOKEN}'
        }
        response = requests.post(slack_api_url, json=modal_data, headers=headers)

        if response.status_code == 200:
            print("Modal Slack API call successful")
        else:
            print("Modal Slack API call failed:", response.text)
    except Exception as e:
        print("Error opening modal:", e)
