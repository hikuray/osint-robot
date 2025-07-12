
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import requests
import urllib.parse

TOKEN = 'ТВОЙ_ТОКЕН_ТЕЛЕГРАМ_БОТА'

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📡 IP", callback_data="ip"),
         InlineKeyboardButton("📧 Email", callback_data="email")],
        [InlineKeyboardButton("🌐 WHOIS", callback_data="whois"),
         InlineKeyboardButton("🔐 SSL", callback_data="ssl")],
        [InlineKeyboardButton("👤 Username", callback_data="username"),
         InlineKeyboardButton("📱 Phone", callback_data="phone")]
    ]
    await update.message.reply_text("🔍 Выберите инструмент OSINT:", reply_markup=InlineKeyboardMarkup(keyboard))

# Выбор инструмента
async def choose_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tool = query.data
    context.user_data["tool"] = tool
    await query.edit_message_text(f"✏️ Введите данные для: {tool.upper()}")

# Обработка пользовательского ввода
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tool = context.user_data.get("tool")
    text = update.message.text.strip()
    context.user_data.clear()

    if tool == "ip":
        msg = lookup_ip(text)
    elif tool == "email":
        msg = lookup_email(text)
    elif tool == "whois":
        msg = f"🌐 WHOIS для {text}:
🔗 https://who.is/whois/{text}"
    elif tool == "ssl":
        msg = f"🔐 SSL-сертификаты для {text}:
🔎 https://crt.sh/?q={text}"
    elif tool == "username":
        msg = lookup_username(text)
    elif tool == "phone":
        msg = lookup_phone(text)
    else:
        msg = "❌ Неизвестный инструмент."

    await update.message.reply_text(msg, disable_web_page_preview=True)

# IP
def lookup_ip(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json").json()
        if 'bogon' in r:
            return "⚠️ Это внутренний или недопустимый IP-адрес."
        return (
            f"📡 *OSINT по IP: {ip}*
"
            f"🌍 Страна: {r.get('country')}
"
            f"🌇 Город: {r.get('city')}
"
            f"📶 Провайдер: {r.get('org')}
"
            f"🗺 Координаты: {r.get('loc')}
"
            f"🔗 [Подробнее](https://ipinfo.io/{ip})"
        )
    except:
        return "❌ Ошибка при получении данных по IP."

# Email
def lookup_email(email):
    encoded = urllib.parse.quote(email)
    return (
        f"📧 *OSINT по Email: {email}*
"
        f"🔍 Ручная проверка утечек:
"
        f"- [HaveIBeenPwned](https://haveibeenpwned.com/account/{encoded})
"
        f"- [Dehashed](https://www.dehashed.com/search?query={encoded})
"
        f"- Google: `site:pastebin.com {email}`
"
        f"- Telegram: `site:telegram.org intext:{email}`"
    )

# Username
def lookup_username(username):
    username = username.lstrip("@")
    return (
        f"👤 *OSINT по Username: {username}*
"
        f"🔗 Telegram: https://t.me/{username}
"
        f"🔗 GitHub: https://github.com/{username}
"
        f"🔗 Instagram: https://instagram.com/{username}
"
        f"🔗 Pastebin: https://pastebin.com/u/{username}
"
        f"🔍 Google: `site:t.me intext:{username}`"
    )

# Phone
def lookup_phone(phone):
    encoded = urllib.parse.quote(phone)
    phone_clean = phone.replace("+", "")
    return (
        f"📱 *OSINT по номеру: {phone}*

"
        f"🔍 Ручная проверка:
"
        f"- [Truecaller](https://www.truecaller.com/search/ru/{phone})
"
        f"- [Numlookup](https://www.numlookup.com/number/{phone_clean})
"
        f"- [Sync.me](https://sync.me/search/?number={encoded})
"
        f"- Google: `site:pastebin.com {phone}`
"
        f"- Telegram: `site:t.me intext:{phone}`"
    )

# Запуск
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_tool))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    print("✅ OSINT Бот запущен.")
    app.run_polling()

if __name__ == '__main__':
    main()
