# auto_forwarder.py

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
import re
import os

# ⛓ .env orqali olingan ma'lumotlar
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")
MANBA1 = os.getenv("MANBA1", "")
MANBA2 = os.getenv("MANBA2", "")
MANBA3 = os.getenv("MANBA3", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
START_HOUR = int(os.getenv("START_HOUR", 7))
END_HOUR = int(os.getenv("END_HOUR", 23))

# 🔎 Faqat to‘ldirilgan manbalarni olamiz
source_channels = [c for c in [MANBA1, MANBA2, MANBA3] if c.strip()]

# 💬 Inline tugma
inline_btn = InlineKeyboardMarkup([[
    InlineKeyboardButton("📢 Yangiliklar 24/7", url="https://t.me/yangiliklar2_4_7")
]])

# 🚀 Pyrogram session
app = Client("reposter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# ❌ Filtrlovchi funksiya
def is_clean_message(text: str) -> bool:
    if not text:
        return True
    lower = text.lower()

    if "reklama" in lower:
        return False
    if "http://" in lower or "https://" in lower:
        return False
    if re.search(r"\+?\d{7,15}", lower):  # Telefon raqami
        return False

    mentions = re.findall(r"@\w+", text)
    for m in mentions:
        if m.lower() != "@tyxuzbek":
            return False
    return True


# 📤 Avto-forward
@app.on_message(filters.channel & filters.chat(source_channels))
async def repost(client: Client, message: Message):
    try:
        # 🕒 Faqat belgilangan vaqt oralig‘ida ishlaydi
        now = datetime.now(pytz.timezone("Asia/Tashkent"))
        if now.hour < START_HOUR or now.hour > END_HOUR:
            return

        caption = message.caption or ""
        caption = caption.replace("@tyxuzbek", "@yangiliklar2_4_7")

        # Ruxsatsiz bo‘lsa — tashlab ketamiz
        if message.photo or message.video:
            if not is_clean_message(caption):
                return
            if message.photo:
                await client.send_photo(
                    chat_id=TARGET_CHANNEL,
                    photo=message.photo.file_id,
                    caption=caption,
                    reply_markup=inline_btn
                )
            else:
                await client.send_video(
                    chat_id=TARGET_CHANNEL,
                    video=message.video.file_id,
                    caption=caption,
                    reply_markup=inline_btn
                )

        elif message.text:
            if not is_clean_message(message.text):
                return
            text = message.text.replace("@tyxuzbek", "@yangiliklar2_4_7")
            await client.send_message(
                chat_id=TARGET_CHANNEL,
                text=text,
                reply_markup=inline_btn
            )

    except Exception as e:
        print(f"[Xatolik] {e}")


# 🔧 /status komandasi (faqat admin uchun)
@app.on_message(filters.command("status") & filters.user(ADMIN_ID))
async def status_handler(client, message):
    await message.reply("✅ Bot ishlayapti va repost xizmati faollashgan.")

# ▶️ Run bot
app.run()
