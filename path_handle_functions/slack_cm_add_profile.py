def handle_add_profile(payload):
    # Extract channel ID from payload
    channel_id = payload.get('channel_id', None)

    # Define message block containing the dropdown menu
    message_block = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":busts_in_silhouette: Add a Profile Url/Profile Urls",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Select the website to enter the add profile url form.",
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an website",
                        
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Medium",
                            },
                            "value": f"{channel_id}___medium",
                        },
                    ],
                    "action_id": "cm_add_profile",
                },
            },
        ],
    }
    return message_block