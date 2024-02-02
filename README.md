# AI_LinkCheckerTelgramBot

## Overview

This project entails the development of a Telegram bot, leveraging the capabilities of the GPT-3.5 language model. The bot is designed to offer link verification services, utilizing artificial intelligence to assess the safety of provided URLs. Additionally, the bot includes administrative functionalities for user management, statistics retrieval, and broadcasting messages.

## Features

1. **Link Verification:**
   - Users can submit URLs for evaluation.
   - The bot employs OpenAI's GPT-3.5 for an AI-driven assessment of the provided links.
   - Results are communicated to users, indicating the safety status of the submitted URLs.

2. **User Management:**
   - The bot keeps track of connected users.
   - Administrators can access user statistics and manage users effectively.

3. **Administrative Controls:**
   - Administrators have exclusive access to commands like `/stats` for retrieving bot statistics.
   - The `/admin` command provides a control panel with various administrative options.

4. **Broadcasting Messages:**
   - Admins can send broadcast messages to all connected users using the `/broadcast` command.

## Commands

- `/start`: Initiates a chat session with the bot.
- `/admin`: Provides access to administrative functions.
- `/stats`: Retrieves statistics related to the bot's usage.
- `/broadcast [message]`: Sends a broadcast message to all connected users.
- `/users`: See all Active Users.
- 

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/d7manDev/AI_LinkCheckerTelgramBot
   ```

2. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the Telegram bot token and OpenAI API key:**
   - Telegram Bot Token: Obtain a token from BotFather on Telegram and replace `[TELEGRAM_BOT_TOKEN]`.
   - OpenAI API Key: Replace `[OPENAI_API_KEY]` with your GPT-3.5 API key.

4. **Run the bot:**

   ```bash
   python Urlbot.py
   ```

5. **User Interaction:**
   - Start a chat with the bot by sending `/start`.
   - Submit a URL for verification by sending the link.
   - Administrators can access administrative functions using `/admin`.



