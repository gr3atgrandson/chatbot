import openai
import sqlite3
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# ===== Configuration =====
# Replace with your OpenAI API key
openai.api_key = "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"
# Replace with your Telegram Bot token
TELEGRAM_BOT_TOKEN = "7624661998:AAGoC_dt767yi3rIGB9IDkmnWIyfFb0R95U"

# ===== Database Setup =====
# Initialize SQLite database
conn = sqlite3.connect('chatbot.db', check_same_thread=False)
cursor = conn.cursor()
# Create table for storing conversations
cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        user_id TEXT, user_message TEXT, bot_response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Save conversations to the database
def store_conversation(user_id, user_message, bot_response):
    cursor.execute('''
        INSERT INTO conversations (user_id, user_message, bot_response) 
        VALUES (?, ?, ?)
    ''', (user_id, user_message, bot_response))
    conn.commit()

# ===== OpenAI GPT Integration =====
def generate_ai_response(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# ===== Web Scraper =====
def scrape_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Example: Get webpage title
        return f"Title: {soup.title.string if soup.title else 'No title found'}"
    except Exception as e:
        return f"Error while scraping: {str(e)}"

# ===== Telegram Bot Handlers =====
# /start command
async def start(update: Update, context):
    await update.message.reply_text("Hello! I am Theta, your AI assistant. Ask me anything or request a web scrape!")

# Message handler
async def respond(update: Update, context):
    user_message = update.message.text
    user_id = update.message.chat_id

    # Check for scraping requests
    if user_message.lower().startswith("scrape"):
        # Extract URL from the message (e.g., "scrape https://example.com")
        parts = user_message.split()
        if len(parts) > 1:
            url = parts[1]
            bot_response = scrape_website(url)
        else:
            bot_response = "Please provide a URL to scrape. Example: scrape https://example.com"
    else:
        # Generate AI response for regular messages
        bot_response = generate_ai_response(user_message)

    # Store the conversation in the database
    store_conversation(user_id, user_message, bot_response)

    # Reply to the user
    await update.message.reply_text(bot_response)

# ===== Main Application =====
if __name__ == "__main__":
    # Create bot application
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))

    # Start the bot
    print("Theta is running...")
    app.run_polling()