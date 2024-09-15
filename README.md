# Telegram Bot

This README provides an overview of the Telegram bot's features and setup instructions.

## Features

1. **Ship Command (`/шип @user1 @user2`):**
   - Ships two users and generates a random ship name.
   - Example usage: `/шип @user1 @user2`.

2. **Context-Aware Responses:**
   - Responds to queries such as `как дела` with context-aware messages.
   - Generates responses based on previous user messages.

3. **Job Commands:**
   - Includes job-related commands with a cooldown of 2 hours on the work command.
   - Example job commands: `/работа` (work command).

4. **Shop:**
   - **Бизнес** (Business): Provides 100 coins every hour and can only be purchased once.
   - **Ускоритель заработка** (Earnings Booster): Reduces cooldown by 30 minutes.
   - **Улучшенный инструмент** (Enhanced Tool): Increases earnings by 20%.

## Setup Instructions

1. **Install Dependencies:**
   Ensure you have `pyTelegramBotAPI`, `requests`, `wikipedia`, and `sqlite3` installed. You can install them using pip:
   ```bash
   pip install pyTelegramBotAPI requests wikipedia-api
