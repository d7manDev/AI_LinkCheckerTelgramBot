import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import datetime
import validators

# Set the API key for OpenAI
openai.api_key = "Your_Openai_Api"  # Replace with your API key

# Set the Telegram bot token
TELEGRAM_BOT_TOKEN = "Your_Bot_Token"  # Replace with your bot token
# Variable to store user information and links
user_data = []
# The user who acts as the bot manager (must be edited according to the actual manager's ID)
ADMIN_USER_ID = Your_Telgram_User_ID
# User configuration (optional)
# USER_ID = 123456789  # Replace with your user ID
control_panel_displayed = False

# Start chat function
def start(update: Update, context: CallbackContext) -> None:
    # Check if the variable is defined, otherwise, define it
    if 'connected_users' not in context.bot_data:
        context.bot_data['connected_users'] = 0

    # Increase the number of connected users by one
    context.bot_data['connected_users'] += 1

    user_info = {
        'user_id': update.message.from_user.id,
        'username': update.message.from_user.username,
        'first_name': update.message.from_user.first_name,
        'last_name': update.message.from_user.last_name,
        'links': []
    }
    user_data.append(user_info)
    # Command list for the side menu
    commands = [
        ['/stats', '/help'],  # You can add more if needed
    ]

    # Set up the side menu buttons
    reply_markup = ReplyKeyboardMarkup(commands, one_time_keyboard=True)

    # If the user is the manager
    if update.message.from_user.id == ADMIN_USER_ID:
        # Special welcome message for the manager
        welcome_message = f'Welcome, ({update.message.from_user.username})! As the bot manager, you can use your special commands.'
        update.message.reply_text(welcome_message)
    else:
        # Regular welcome message for ordinary users
        welcome_message = f'Welcome, ({update.message.from_user.username})! Send the link you want to check.'
        update.message.reply_text(welcome_message)
        # Welcome message and developer info in the same reply and in two lines with list formatting
    welcome_and_developer_message = (
        f'Welcome, ({update.message.from_user.username})!\n'
        f'- This bot was programmed and developed by @D7g_x.'
    )
    update.message.reply_text(welcome_and_developer_message)
    # Send a guidance message to the user
    guidance_message = 'You can start the check by sending the link you want to examine.'
    update.message.reply_text(guidance_message)

# Check URL function
def check_url(update: Update, context: CallbackContext) -> None:
    global total_links_sent, total_response_time
    # Check user identity (optional)
    user_id = update.message.from_user.id

    # Extract the link from the message
    url = update.message.text

    # Check the validity of the link using the validators library
    if not validators.url(url):
        update.message.reply_text('Please enter a valid link.')
        return
    # Send a "typing" message
    typing_message = context.bot.send_message(chat_id=update.effective_chat.id, text='Checking the link now...')

    # Generate the response from OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"Please review this link: {url}. As a cybersecurity consultant, consider various factors related to the given link. Respond in the following format. [Part A, Part B]. Where Part A can only be either good or bad, without providing any other explanations for this part. Choose good if the link does not appear to be a phishing link, and choose bad otherwise. As for Part B, it is the reason for explaining Part A."
            }
        ]
    )
    # Delete the "typing" message
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=typing_message.message_id)
    # Extract the result and send it to the user
    result = response['choices'][0]['message']['content']
    update.message.reply_text(f"Link assessment: {result}")
    # Send a thank-you message
    update.message.reply_text('Thank you for using the AI-powered link verification bot.')
    # Log information in the terminal
    print(f"User: {user_id}, Link: {url}, Assessment: {result}")

    # Log information in the log file
    with open('log.txt', 'a') as log_file:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"{timestamp} - User: {user_id}, Link: {url}, Assessment: {result}\n")
# Statistics function
def stats(update: Update, context: CallbackContext) -> None:
    # Confirm that the user is the manager
    if update.message.from_user.id != ADMIN_USER_ID:
        update.message.reply_text('You do not have permissions to use this command.')
        return

    total_users = len(user_data)
    total_links_sent = sum(len(user.get('links', [])) for user in user_data)
    average_response_time = calculate_average_response_time(user_data)

    stats_message = (
        f'Bot Statistics:\n'
        f'Total connected users: {total_users}\n'
        f'Total links sent: {total_links_sent}\n'
        f'Average response time: {average_response_time} seconds'
    )

    # Send the statistics message
    update.message.reply_text(stats_message)
    # Function to handle interactive buttons
def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'cancel':
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=query.message.message_id)
def calculate_average_response_time(user_data):
    # Use user_data to get response times for each user
    response_times = [user.get('response_time', 0) for user in user_data]

    # Calculate the average
    average_time = sum(response_times) / len(response_times) if len(response_times) > 0 else 0

    return round(average_time, 2)  # Round the value to the nearest two decimals
# Function to send a broadcast message to all users
def send_broadcast_message(update: Update, context: CallbackContext) -> None:
    # Check if the user is the admin
    if update.message.from_user.id != ADMIN_USER_ID:
        return
    
    # Extract the message from the command
    message_text = ' '.join(context.args)

    # Check if the message text is not empty
    if not message_text:
        update.message.reply_text('Please provide a message to broadcast.')
        return

    # Get all users from user_data
    users = [user['user_id'] for user in user_data]

    # Send the broadcast message to all users
    for user_id in users:
        context.bot.send_message(chat_id=user_id, text=message_text)

    # Notify the admin about the successful broadcast
    update.message.reply_text(f'Broadcast message sent to {len(users)} users successfully.')
# Administrative function
def admin(update: Update, context: CallbackContext) -> None:
    # If the user is not the manager, do nothing
    if update.message.from_user.id != ADMIN_USER_ID:
        return

    # Set up the list of actions that the manager can perform
    available_actions = [
        {'name': 'User Management', 'callback_data': 'user_management'},
        {'name': 'Send Promotion', 'callback_data': 'send_promotion'},
        {'name': 'Security Log', 'callback_data': 'security_log'},
    ]

    # Set up buttons with the names of the actions
    buttons = [InlineKeyboardButton(action['name'], callback_data=action['callback_data']) for action in available_actions]

    # Divide the buttons into rows
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    # Set up the panel based on the divided buttons
    control_markup = InlineKeyboardMarkup(rows)

    # Send a message with control buttons
    update.message.reply_text('Choose one of the options:', reply_markup=control_markup)
def main() -> None:
    updater = Updater(token=TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    url_handler = MessageHandler(Filters.text & ~Filters.command, check_url)
    dispatcher.add_handler(url_handler)

    admin_handler = CommandHandler("admin", admin)
    dispatcher.add_handler(admin_handler)

    control_handler = CallbackQueryHandler(button_callback)
    dispatcher.add_handler(control_handler)
    dispatcher.add_handler(CommandHandler("stats", stats))

    broadcast_handler = CommandHandler("broadcast", send_broadcast_message)
    dispatcher.add_handler(broadcast_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
