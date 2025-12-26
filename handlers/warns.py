from pyrogram import filters
from database.warns import add_warn, reset_warn
from utils.typing import typing

WARN_LIMIT = 3

def register_warns(app):

    @app.on_message(filters.command("warn") & filters.group)
    async def warn_user(client, message):
        if not message.reply_to_message:
            return await message.reply("Reply to a user to warn.")
        user = message.reply_to_message.from_user
        await typing(client, message.chat.id)

        count = await add_warn(message.chat.id, user.id)

        if count >= WARN_LIMIT:
            await message.chat.ban_member(user.id)
            await reset_warn(message.chat.id, user.id)
            await message.reply(f"🚫 {user.mention} banned (warn limit).")
        else:
            await message.reply(f"⚠️ {user.mention} warned ({count}/{WARN_LIMIT}).")
