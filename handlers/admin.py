from pyrogram import filters
from utils.typing import typing

def register_admin(app):

    @app.on_message(filters.command("pin") & filters.group)
    async def pin_msg(client, message):
        if not message.reply_to_message:
            return await message.reply("Reply to a message to pin.")
        await typing(client, message.chat.id)
        await message.reply_to_message.pin()
        await message.reply("📌 Pinned.")
