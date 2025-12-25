import logging
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================== ضع التوكن هنا ==================
BOT_TOKEN = "8401774647:AAF0UXAoe97oy_zuODBJLFwVwf8OQBqZCwc"

# ================== ملفات الإكسل ==================
HEAVY_FILE = "heavy.xlsx"
SPARE_FILE = "spare.xlsx"

USD_TO_IQD = 1400

# ================== لوق ==================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ================== تحميل البيانات ==================
def load_excel(path):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    return df

heavy_df = load_excel(HEAVY_FILE)
spare_df = load_excel(SPARE_FILE)

# ================== أدوات ==================
def price_iqd(price):
    try:
        return int(float(price) * USD_TO_IQD)
    except:
        return "غير محدد"

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔍 بحث"],
        ["📋 عرض القائمة"],
    ]
    await update.message.reply_text(
        "👋 أهلاً بك في بوت البحث بالمخزن\nاختر من القائمة:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

# ================== عرض القائمة ==================
async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 قائمة المواد (الثقيلة):\n\n"
    for _, row in heavy_df.iterrows():
        text += f"- {row['اسم المادة']} (الكمية: {row['الإعداد الموجودة']})\n"

    await update.message.reply_text(text)

# ================== البحث ==================
async def ask_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["search"] = True
    await update.message.reply_text("✏️ أرسل اسم المادة أو الباركود:")

async def do_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    found = False

    for df, section in [(heavy_df, "ثقيل"), (spare_df, "احتياطية")]:
        result = df[
            (df["اسم المادة"].astype(str).str.contains(query, case=False, na=False))
            | (df["الباركود"].astype(str) == query)
        ]

        if not result.empty:
            row = result.iloc[0]
            msg = (
                f"📦 الاسم: {row['اسم المادة']}\n"
                f"🏷️ الباركود: {row['الباركود']}\n"
                f"📊 الكمية: {row['الإعداد الموجودة']}\n"
                f"💰 السعر: {price_iqd(row['السعر'])} د.ع\n"
                f"📁 القسم: {section}"
            )
            await update.message.reply_text(msg)
            found = True
            break

    if not found:
        await update.message.reply_text("❌ لم يتم العثور على المادة.")

# ================== استقبال الرسائل ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📋 عرض القائمة":
        await show_list(update, context)

    elif text == "🔍 بحث":
        await ask_search(update, context)

    elif context.user_data.get("search"):
        context.user_data["search"] = False
        await do_search(update, context)

# ================== تشغيل البوت ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
