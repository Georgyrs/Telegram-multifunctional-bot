Telegram Bot 
Overview
This Telegram bot is designed to enhance the experience for the class community. It provides various interactive features including creating ships (relationships), checking weather updates, managing events, performing jobs for rewards, and more. The bot integrates with Wikipedia for information retrieval and supports a custom shop system for purchasing upgrades.

Features
Welcome Message: Welcomes new members to the chat.
Ship Creation: Allows users to create "ships" (relationships) between two users.
Event Management: Create and manage important events.
Weather Updates: Provides current weather conditions and advice.
Random Facts: Sends random facts to users.
Jobs and Earnings: Users can perform jobs to earn virtual currency with a cooldown period.
Upgrades: Users can purchase upgrades that enhance their earnings or provide other benefits.
Balance Check: Users can check their virtual balance.
Wikipedia Search: Provides summaries from Wikipedia based on user queries.
Setup
Prerequisites
Python 3.6+: Ensure you have Python 3.6 or higher installed.
Required Libraries: Install the necessary libraries using pip:
bash
Копировать код
pip install requests beautifulsoup4 wikipedia-api pyTelegramBotAPI sqlite3
Configuration
Create a config.py file with the following content and fill in your credentials:
python
Копировать код
BOT_TOKEN = 'your_telegram_bot_token'
WIKIPEDIA_LANGUAGE = 'ru'  # Language code for Wikipedia
WEATHER_URL = 'your_weather_website_url'
WEATHER_API_URL = 'your_weather_api_url'
DATABASE_NAME = 'bot_database.db'
MEDIA_PATHS = {
    1: 'path/to/image1.jpg',
    2: 'path/to/image2.jpg',
    3: 'path/to/video1.mp4',
    4: 'path/to/video2.mp4',
    5: 'path/to/image3.png',
    6: 'path/to/image4.jpeg'
}
Database Initialization
The bot initializes the SQLite database upon startup with the following tables:
ships: Stores ship data between users.
events: Stores event data.
users: Stores user balances.
jobs: Stores job information.
upgrades: Stores upgrade details.
user_upgrades: Stores user-specific upgrades.
message_stats: Stores message statistics for tracking.
Running the Bot
To run the bot, execute the following command:

bash
Копировать код
python your_bot_file.py
Commands
General Commands
/start: Starts the bot and provides a welcome message.
/руководство: Displays a list of available commands and their usage.
Ship Commands
/шип @user1 @user2: Creates a ship between two users.
/список шипов: Displays a list of all ships.
Event Commands
/событие_создать дата событие: Creates an event on a specified date.
/даты: Displays all upcoming events.
Weather Commands
/погода: Provides the current weather and advice.
Wikipedia Commands
/списать <запрос>: Retrieves a summary from Wikipedia for the given query.
Job Commands
/работать: Performs a job and earns virtual currency. (Cooldown: 2 hours)
Shop Commands
/шоп: Opens the shop for purchasing upgrades.
Balance Commands
/кошелек: Checks the user's current balance.
Upgrades
Users can purchase the following upgrades:

Ускоритель заработка: Increases earnings from jobs by 50%.
Улучшенный инструмент: Increases earnings by 20%.
Бизнес: Provides 100 coins every hour.
Contributing
If you'd like to contribute to this project, please fork the repository and submit a pull request with your changes.

License
This project is licensed under the MIT License - see the LICENSE file for details.

