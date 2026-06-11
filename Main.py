import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from openai import OpenAI

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Configuration
client = OpenAI(api_key='YOUR_OPENAI_API_KEY')
BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# State definitions
BUSINESS_NAME, STYLE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Lookabot! What is the name of your business?")
    return BUSINESS_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Great! What style or industry should the logo represent? (e.g., minimalist tech, rustic bakery)")
    return STYLE

async def generate_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    style = update.message.text
    name = context.user_data['name']
    
    await update.message.reply_text("Generating your logo... please wait.")

    # Generate image using DALL-E 3
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"A professional high-quality logo for a business named '{name}'. The style is {style}. Clean vector graphic, white background.",
        n=1,
        size="1024x1024"
    )
    
    image_url = response.data[0].url
    await update.message.reply_photo(photo=image_url, caption=f"Here is your logo for {name}!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Process cancelled.")
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
