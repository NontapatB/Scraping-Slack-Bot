from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from pathlib import Path
from dotenv import load_dotenv
import os
import requests

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve Slack token from environment variables
SLACK_TOKEN = os.environ['SLACK_TOKEN']

# Function to send a message to a Slack channel
def send_slack_message(channel, message):
    # Initialize a WebClient instance with the Slack token
    client = WebClient(token=SLACK_TOKEN)
    try:
        # Send the message to the specified channel
        response = client.chat_postMessage(
            channel=channel,
            text=message
        )
        print("Message sent to Slack successfully:", response['ts'])
    except SlackApiError as e:
        # Handle errors if the message sending fails
        print(f"Failed to send message to Slack. Error: {e.response['error']}")

# Function to send an ephemeral message to a Slack user
def send_slack_invisible_message(channel_id, user_id, response_text):
    # Define the payload for the API request
    payload = {
        "channel": channel_id,
        "user": user_id,
        "text": response_text,
    }
    # Send the POST request to the Slack API for ephemeral messages
    response = requests.post("https://slack.com/api/chat.postEphemeral", json=payload, headers={"Authorization": f"Bearer {SLACK_TOKEN}"})

    # Check if the request was successful
    if response.status_code == 200 and response.json().get('ok'):
        print(f"Message sent successfully to user {user_id}")
    else:
        # Handle errors if the message sending fails
        print(f"Failed to send message to user {user_id}. Error: {response.text}")