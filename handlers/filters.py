from pyrogram import filters
from database.filters import add_filter, remove_filter, get_filters
from utils.typing import typing

def register_filters(app):

    # /filter hello Hi there!
    @app.on_message(filters.command("filter") & filters.group)
    async def add(_, message):
        if len(message.command) < 3:
            return await message.reply("Usage: /filter <word> <reply>")
        word = message.command[1].lower()
        reply = message.text.split(None, 2)[2]
        await add_filter(message.chat.id, word, reply)
        await message.reply(f"✅ Filter added for `{word}`")

    # /stop hello
    @app.on_message(filters.command("stop") & filters.group)
    async def stop(_, message):
        if len(message.command) < 2:
            return await message.reply("Usage: /stop <word>")
        word = message.command[1].lower()
        await remove_filter(message.chat.id, word)
        await message.reply(f"❌ Filter `{word}` removed")

    # /filters
    @app.on_message(filters.command("filters") & filters.group)
    async def list_filters(_, message):
        data = []
        async for f in await get_filters(message.chat.id):
            data.append(f"• `{f['keyword']}`")
        await message.reply(
            "🧠 **Active Filters**\n\n" + ("\n".join(data) if data else "No filters.")
        )

    # Auto reply when keyword appears
    @app.on_message(filters.group & filters.text)
    async def watch(client, message):
        text = message.text.lower()
        async for f in await get_filters(message.chat.id):
            if f["keyword"] in text:
                await typing(client, message.chat.id, 1)
                await message.reply(f["reply"])
                break
