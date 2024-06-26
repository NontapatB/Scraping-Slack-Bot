﻿# Scraping-Slack-Bot

# NewsBot

![logo-slackbot](images/slack_bot_logo-removebg-preview.png)

Hi!, This project was developed as part of a training program. As a trainee, the developer aimed to enhance skills in Python programming, web scraping, and bot development. NewsBot serves as a demonstration of their abilities to create a functional tool that integrates with Slack to deliver daily news updates.

*NewsBot* is a Slack bot that helps to update news from various websites, allowing users to receive the latest news daily and conveniently through Slack communication channels.

## Installation

1. **Set up the bot in Slack:** Create a bot in Slack and obtain the API token for usage.
![create-app](images/create-app.png)

![create-app](images/create-app2.png)

![enable-scope](images/scope.png)

![slash-command](images/slash-command.png)

![slash-command](images/example-slash.png)

3. **Install on your server:** Download the NewsBot code and install necessary dependencies.
4. **Configure settings:** Enter the Slack token obtained in step 1 and configure other settings as needed.
5. **Run the bot:** Start using NewsBot on your server.

## Usage

1. **Call NewsBot:** Simply mention the name of the bot in Slack and invoke various commands.
2. **Receive information:** Use predefined commands to receive news data from desired websites.

## Example

- `/bookmarks`: Show all bookmarks url.
- `/help`: Help command will show details of all commands.
- `/all_profiles`: Show all profile urls that added by users.
- `/all_categories`: Show all categories that added by users.
- `/add_profile`: Select website to enter the add form.
- `/add_category`: Select website to enter the add form.

## System Requirements

- Python 3.8 or above
- Dependencies: [SlackClient](https://github.com/slackapi/python-slackclient), [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- others from requirements.txt

## Future Updates

- **Facebook Page Scraping:** Implement scraping functionality to gather news updates from Facebook pages, expanding NewsBot's coverage of social media platforms.
- **Generative AI Integration:** Utilize Generative AI technology to provide more personalized news summaries and recommendations, enhancing the user experience by delivering relevant content tailored to individual preferences.

## Conclusion

Thank you for using *NewsBot*! If you have any questions or suggestions, please contact us at b.nontapat.work@gmail.com.
