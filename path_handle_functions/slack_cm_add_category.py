def handle_add_category(payload):
    # Extract channel ID from payload
    channel_id = payload.get('channel_id', None)

    # Define message block containing the dropdown menu
    message_block = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":earth_asia: Add a Category/Categories",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Select the website to enter the add category form.",
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
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Somkiat.cc",
                            },
                            "value": f"{channel_id}___somkiat",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Facebook Dev. Community",
                            },
                            "value": f"{channel_id}___facebook",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Akexorcist",
                            },
                            "value": f"{channel_id}___akexorcist",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Techtalkthai",
                            },
                            "value": f"{channel_id}___techtalkthai",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Blognone",
                            },
                            "value": f"{channel_id}___blognone",
                        },
                    ],
                    "action_id": "cm_add_category",
                },
            },
        ],
    }
    return message_block