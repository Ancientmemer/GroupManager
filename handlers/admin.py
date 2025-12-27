from pyrogram import filters
from pyrogram.types import ChatPermissions
from utils.typing import typing


def register_admin(app):

    # ==================================================
    # UNIVERSAL ADMIN CHECK (ALL TELEGRAM CASES)
    # ==================================================
    async def is_admin(client, message):
        # Case 1: Sent as channel / group
        if message.sender_chat:
            return True

        # Case 2: Anonymous admin
        if message.from_user is None:
            return True

        # Case 3: Normal admin
        member = await client.get_chat_member(
            message.chat.id,
            message.from_user.id
        )
        return member.status in ("administrator", "owner")

    async def is_bot_admin(client, chat_id):
        me = await client.get_chat_member(chat_id, "me")
        return me.status in ("administrator", "owner")

    # ==================================================
    # BAN
    # ==================================================
    @app.on_message(filters.command("ban") & filters.group)
    async def ban(client, message):
        if not message.reply_to_message:
            return await message.reply("❗ Reply to a user to ban.")

        if not await is_admin(client, message):
            return await message.reply("❌ You are not an admin.")

        if not await is_bot_admin(client, message.chat.id):
            return await message.reply("❌ I am not admin.")

        user_id = message.reply_to_message.from_user.id
        await typing(client, message.chat.id)

        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply("🚫 User banned.")

    # ==================================================
    # UNBAN
    # ==================================================
    @app.on_message(filters.command("unban") & filters.group)
    async def unban(client, message):
        if not message.reply_to_message:
            return await message.reply("❗ Reply to a user to unban.")

        if not await is_admin(client, message):
            return await message.reply("❌ You are not an admin.")

        if not await is_bot_admin(client, message.chat.id):
            return await message.reply("❌ I am not admin.")

        user_id = message.reply_to_message.from_user.id

        await client.unban_chat_member(
            message.chat.id,
            user_id,
            only_if_banned=False
        )
        await message.reply("✅ User unbanned.")

    # ==================================================
    # MUTE
    # ==================================================
    @app.on_message(filters.command("mute") & filters.group)
    async def mute(client, message):
        if not message.reply_to_message:
            return await message.reply("❗ Reply to a user to mute.")

        if not await is_admin(client, message):
            return await message.reply("❌ You are not an admin.")

        if not await is_bot_admin(client, message.chat.id):
            return await message.reply("❌ I am not admin.")

        user_id = message.reply_to_message.from_user.id
        await typing(client, message.chat.id)

        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions()
        )
        await message.reply("🔇 User muted.")

    # ==================================================
    # UNMUTE
    # ==================================================
    @app.on_message(filters.command("unmute") & filters.group)
    async def unmute(client, message):
        if not message.reply_to_message:
            return await message.reply("❗ Reply to a user to unmute.")

        if not await is_admin(client, message):
            return await message.reply("❌ You are not an admin.")

        if not await is_bot_admin(client, message.chat.id):
            return await message.reply("❌ I am not admin.")

        user_id = message.reply_to_message.from_user.id

        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await message.reply("🔊 User unmuted.")

    # ==================================================
    # PURGE
    # ==================================================
    @app.on_message(filters.command("purge") & filters.group)
    async def purge(client, message):
        if not message.reply_to_message:
            return await message.reply("❗ Reply to a message to start purge.")

        if not await is_admin(client, message):
            return await message.reply("❌ You are not an admin.")

        if not await is_bot_admin(client, message.chat.id):
            return await message.reply("❌ I am not admin.")

        start = message.reply_to_message.id
        end = message.id

        message_ids = list(range(start, end + 1))
        await client.delete_messages(message.chat.id, message_ids)

        await message.reply("🧹 Messages purged.")
