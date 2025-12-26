from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.typing import typing

def register_start(app):

    @app.on_message(filters.command("start") & filters.private)
    async def start_private(client, message):
        await typing(client, message.chat.id, 2)

        text = (
            "🌹 **Rose-Style Group Manager Bot** 🌹\n\n"
            "👮 Admin tools\n"
            "⚠️ Warn system + auto ban\n"
            "🔒 Anti-link / Anti-spam\n"
            "🧠 Filters & Notes\n"
            "📌 Pin / Purge / Welcome\n\n"
            "➕ **Add me to your group and promote as admin**\n"
            "Then use `/help` inside the group 😌"
        )

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "➕ Add to Group",
                    url=f"https://t.me/{client.me.username}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton("📚 Help", callback_data="help")
            ]
        ])

        await message.reply_text(text, reply_markup=buttons)

    @app.on_message(filters.command("start") & filters.group)
    async def start_group(_, message):
        await message.reply(
            "👋 **Hello!**\n"
            "I'm active and ready to manage this group 🌹\n"
            "Use `/help` to see commands."
        )
