from pyrogram import filters
from utils.admin import is_admin
from database.connections import set_connection, clear_connection


def register_connect(app):

    @app.on_message(filters.command("connect") & filters.private)
    async def connect_group(client, message):
        if len(message.command) < 2:
            return await message.reply(
                "❗ Usage:\n/connect <group_id>"
            )

        try:
            group_id = int(message.command[1])
        except ValueError:
            return await message.reply("❌ Invalid group ID.")

        # Check bot is in group
        try:
            chat = await client.get_chat(group_id)
        except:
            return await message.reply("❌ Bot is not in that group.")

        # Check admin permission
        fake = type("obj", (), {})()
        fake.chat = chat
        fake.from_user = message.from_user
        fake.sender_chat = None

        if not await is_admin(client, fake):
            return await message.reply(
                "❌ You must be an admin of that group."
            )

        await set_connection(message.from_user.id, group_id)

        await message.reply(
            f"✅ **Connected successfully!**\n\n"
            f"🔗 Group: **{chat.title}**\n\n"
            f"You can now manage filters here in PM."
        )

    @app.on_message(filters.command("disconnect") & filters.private)
    async def disconnect_group(client, message):
        await clear_connection(message.from_user.id)
        await message.reply("🔌 Disconnected from group.")
