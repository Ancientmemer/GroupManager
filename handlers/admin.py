from pyrogram import filters
from pyrogram.types import ChatPermissions
from utils.admin import is_admin
from utils.typing import typing
from database.warns import (
    add_warn,
    remove_one_warn,
    get_warn_count
)

# =========================
# DEFAULT WARN LIMIT
# =========================
DEFAULT_WARN_LIMIT = 3
WARN_LIMITS = {}


def register_admin(app):

    # =========================
    # HELPER: GET TARGET USER
    # =========================
    async def get_target_user(client, message):
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user

        if len(message.command) >= 2:
            try:
                return await client.get_users(message.command[1])
            except:
                return None
        return None

    # =========================
    # HELPER: PARSE REASON
    # =========================
    def parse_reason(message, start):
        if len(message.command) > start:
            return " ".join(message.command[start:])
        return None

    # =========================
    # WARN LIMIT
    # =========================
    @app.on_message(filters.command("warnlimit") & filters.group)
    async def warnlimit(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if len(message.command) < 2 or not message.command[1].isdigit():
            return await message.reply("❗ Usage: /warnlimit <number>")

        WARN_LIMITS[message.chat.id] = int(message.command[1])
        await message.reply(f"⚠️ Warn limit set to {message.command[1]}")

    # =========================
    # WARN
    # =========================
    @app.on_message(filters.command("warn") & filters.group)
    async def warn(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Reply or mention a user.")

        reason = parse_reason(message, 2 if not message.reply_to_message else 1)

        await typing(client, message.chat.id)
        count = await add_warn(message.chat.id, user.id)
        limit = WARN_LIMITS.get(message.chat.id, DEFAULT_WARN_LIMIT)

        if count >= limit:
            await client.ban_chat_member(message.chat.id, user.id)
            await message.reply(f"🚫 {user.mention} banned (warn limit reached)")
        else:
            text = f"⚠️ {user.mention} warned ({count}/{limit})"
            if reason:
                text += f"\n📝 Reason: {reason}"
            await message.reply(text)

    # =========================
    # REMOVE ONE WARN
    # =========================
    @app.on_message(filters.command("rmwarn") & filters.group)
    async def rmwarn(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Reply or mention a user.")

        new = await remove_one_warn(message.chat.id, user.id)
        await message.reply(
            f"✅ One warn removed from {user.mention}\n"
            f"⚠️ Current warns: {new}"
        )

    # =========================
    # WARNINGS
    # =========================
    @app.on_message(filters.command("warnings") & filters.group)
    async def warnings(client, message):
        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Reply or mention a user.")

        count = await get_warn_count(message.chat.id, user.id)
        await message.reply(f"⚠️ {user.mention} has {count} warning(s).")

    # =========================
    # BAN
    # =========================
    @app.on_message(filters.command("ban") & filters.group)
    async def ban(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Reply or mention a user.")

        reason = parse_reason(message, 2 if not message.reply_to_message else 1)
        await client.ban_chat_member(message.chat.id, user.id)

        text = f"🚫 {user.mention} banned."
        if reason:
            text += f"\n📝 Reason: {reason}"
        await message.reply(text)

    # =========================
    # UNBAN
    # =========================
    @app.on_message(filters.command("unban") & filters.group)
    async def unban(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Mention a user.")

        await client.unban_chat_member(message.chat.id, user.id)
        await message.reply(f"✅ {user.mention} unbanned.")

    # =========================
    # MUTE
    # =========================
    @app.on_message(filters.command("mute") & filters.group)
    async def mute(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Reply or mention a user.")

        perms = ChatPermissions(can_send_messages=False)
        await client.restrict_chat_member(message.chat.id, user.id, perms)
        await message.reply(f"🔇 {user.mention} muted.")

    # =========================
    # UNMUTE
    # =========================
    @app.on_message(filters.command("unmute") & filters.group)
    async def unmute(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Reply or mention a user.")

        perms = ChatPermissions(can_send_messages=True)
        await client.restrict_chat_member(message.chat.id, user.id, perms)
        await message.reply(f"🔊 {user.mention} unmuted.")

    # =========================
    # PIN
    # =========================
    @app.on_message(filters.command("pin") & filters.group)
    async def pin(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply("❗ Reply to a message to pin.")

        await client.pin_chat_message(
            message.chat.id,
            message.reply_to_message.id
        )
        await message.reply("📌 Message pinned.")

    # =========================
    # PURGE (reply based)
    # =========================
    @app.on_message(filters.command("purge") & filters.group)
    async def purge(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply("❗ Reply to a message to start purge.")

        start = message.reply_to_message.id
        end = message.id

        for msg_id in range(start, end + 1):
            try:
                await client.delete_messages(message.chat.id, msg_id)
            except:
                pass
