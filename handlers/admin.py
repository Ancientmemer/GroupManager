from pyrogram import filters
from pyrogram.types import ChatPermissions
from utils.typing import typing


def register_admin(app):

    # =========================
    # ADMIN CHECK
    # =========================
    async def is_admin(client, chat_id, user_id):
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "owner")

    # =========================
    # BAN
    # =========================
    @app.on_message(filters.group & filters.command("ban"))
    async def ban(client, message):
        if not message.from_user:
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply("❗ Reply to a user to ban.")

        await typing(client, message.chat.id)
        user_id = message.reply_to_message.from_user.id
        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply("🚫 User banned.")

    # =========================
    # UNBAN
    # =========================
    @app.on_message(filters.group & filters.command("unban"))
    async def unban(client, message):
        if not message.from_user:
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply("❗ Reply to a user to unban.")

        user_id = message.reply_to_message.from_user.id
        await client.unban_chat_member(message.chat.id, user_id, only_if_banned=False)
        await message.reply("✅ User unbanned.")

    # =========================
    # MUTE
    # =========================
    @app.on_message(filters.group & filters.command("mute"))
    async def mute(client, message):
        if not message.from_user:
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply("❗ Reply to a user to mute.")

        await typing(client, message.chat.id)
        user_id = message.reply_to_message.from_user.id
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions()
        )
        await message.reply("🔇 User muted.")

    # =========================
    # UNMUTE
    # =========================
    @app.on_message(filters.group & filters.command("unmute"))
    async def unmute(client, message):
        if not message.from_user:
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply("❗ Reply to a user to unmute.")

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

    # =========================
    # PURGE
    # =========================
    @app.on_message(filters.group & filters.command("purge"))
    async def purge(client, message):
        if not message.from_user:
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply("❗ Reply to a message to start purge.")

        start = message.reply_to_message.id
        end = message.id
        message_ids = list(range(start, end + 1))
        await client.delete_messages(message.chat.id, message_ids)
        await message.reply("🧹 Messages purged.")
