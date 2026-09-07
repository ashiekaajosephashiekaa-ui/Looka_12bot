import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 🔐 Read token from environment (NEVER hardcode it)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# Conversation states
BUSINESS_NAME, STYLE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Lookabot! 🎨\nWhat is the name of your business?")
    return BUSINESS_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Great! What style should the logo represent? (e.g., modern, rustic, colorful)")
    return STYLE

async def generate_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    style = update.message.text
    name = context.user_data['name']
    
    # 🖼️ Try to send a high-resolution image from your repo
    # Place a file named "logo.png" in the root of your GitHub repo
    if os.path.exists("logo.png"):
        await update.message.reply_text(f"Generating your HD logo for '{name}'... ✨")
        with open("logo.png", "rb") as photo_file:
            await update.message.reply_photo(
                photo=photo_file,
                caption=f"✅ Here is your high-resolution logo for **{name}**!\nStyle: {style}\n\n*(Upload your own 'logo.png' to change this image)*"
            )
    else:
        # Fallback if no image is found
        await update.message.reply_text(
            f"📝 Business: {name}\n🎨 Style: {style}\n\n"
            "To send an HD logo, please upload a high-res `logo.png` to the bot's repository."
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Process cancelled. Start again with /start")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BUSINESS_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_logo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(conv_handler)
    app.run_polling()
