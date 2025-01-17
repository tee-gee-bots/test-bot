# src/bot.py
import asyncio
import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
MY_BOT_NAME='test-bot'  # Update me first!
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(MY_BOT_NAME)

# API configuration from environment
API_ENDPOINT = os.getenv('API_ENDPOINT')

async def health_check():
    """Check bot's health and API connection."""
    try:
        api_url = f"{API_ENDPOINT}/health"
        logger.info(f"Checking API health at: {api_url}")
        
        response = requests.get(api_url, timeout=5)
        logger.info(f"API Response: {response.status_code} - {response.text}")
        api_status = response.status_code == 200
        
        result = {
            "status": "healthy",
            "api_connected": api_status,
            "api_endpoint": API_ENDPOINT,
            "api_status_code": response.status_code,
            "api_response": response.text
        }
        logger.info(f"Health check result: {result}")
        return result
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "api_endpoint": API_ENDPOINT
        }

# Docker healthcheck
from aiohttp import web
async def handle_health(request):
    health = await health_check()
    status = 200 if health["status"] == "healthy" else 500
    return web.json_response(health, status=status)

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(f'Hello! I am your test bot. My name is {MY_BOT_NAME}')

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /ping is issued."""
    await update.message.reply_text('Pong!')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/ping - Check if bot is running
    """
    await update.message.reply_text(help_text)


def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logging.error('No TELEGRAM_TOKEN provided')
        return

    # Create application
    application = Application.builder().token(token).build()

    # Add command handlers (starts with /your-command)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("ping", ping))

    # Start health check server
    app = web.Application()
    app.router.add_get('/health', handle_health)
    runner = web.AppRunner(app)

    async def start_health_server():
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()

    # Run both the bot and health server
    asyncio.get_event_loop().run_until_complete(start_health_server())
    application.run_polling()

if __name__ == '__main__':
    main()
