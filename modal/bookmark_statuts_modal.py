import requests
from flask import request
from pathlib import Path
from dotenv import load_dotenv
from flask import jsonify
import os

from path_handle_functions.slack_cm_bookmarks import handle_bookmarks

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve environment variables
SLACK_TOKEN = os.environ['SLACK_TOKEN']

def open_bookmark_status_modal(trigger_id, value):
    payload = request.form.to_dict()
    print('asasd;as;da;ds', payload)
    print('test value',value)
    user_name, blog_url= str(value).split('___')
    try:
        # Define the data for the modal view
        modal_data = {
            "trigger_id": trigger_id,
            "view" : {
                "title": {
                    "type": "plain_text",
                    "text": "Edit Bookmark Status",
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Submit",
                },
                "type": "modal",
                "close": {
                    "type": "plain_text",
                    "text": "Cancel",
                },
                "blocks": [
                    {
                        "type": "input",
                        "element": {
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select a status",
                            },
                            
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Not Read",
                                    },
                                    "value": "Not Read"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Reading",
                                    },
                                    "value": "Reading"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Read",
                                    },
                                    "value": "Read"
                                }
                            ],
                            "action_id": "static_select-action_bookmark_status",
                             
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Select a status here",
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": "*If the status is not updated, please try typing command /bookmarks again",
                        }
                    },
                ],
                "private_metadata": f'{user_name}___{blog_url}',
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
    # return handle_bookmarks(user_name, 'C06C8PR9M9Q')