from pyrogram import filters
from utils.admin import is_admin
from database.connections import (
    set_connection,
    get_connection,
    clear_connection
)


def register_connect(app):

    @app.on_message(filters.command("connect") & filters.private)
    async def connect(client, message):

        if len(message.command) < 2:
            return await message.reply("❗ Usage:\n`/connect <group_id>`")

        try:
            group_id = int(message.command[1])
        except:
            return await message.reply("❌ Invalid group id.")

        # Fake chat object for admin check
        class FakeChat:
            id = group_id

        fake_message = message
        fake_message.chat = FakeChat()

        if not await is_admin(client, fake_message):
            return await message.reply("❌ You must be admin of that group.")

        await set_connection(message.from_user.id, group_id)

        try:
            chat = await client.get_chat(group_id)
            name = chat.title
        except:
            name = str(group_id)

        await message.reply(
            f"✅ **Connected successfully**\n\n"
            f"🔗 Group: **{name}**\n\n"
            f"You can now manage filters from PM."
        )

    @app.on_message(filters.command("disconnect") & filters.private)
    async def disconnect(client, message):

        data = await get_connection(message.from_user.id)
        if not data:
            return await message.reply("ℹ️ Not connected to any group.")

        await clear_connection(message.from_user.id)
        await message.reply("🔌 Disconnected successfully.")
