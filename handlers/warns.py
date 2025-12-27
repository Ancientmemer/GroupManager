from pyrogram import filters
from database.warns import add_warn, reset_warn
from utils.typing import typing

# =========================
# DEFAULT WARN LIMIT
# =========================
DEFAULT_WARN_LIMIT = 3

# Per-group warn limits (in-memory)
WARN_LIMITS = {}


def register_warns(app):

    # =========================
    # ADMIN CHECK
    # =========================
    async def is_admin(client, chat_id, user_id):
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "owner")

    # =========================
    # RESOLVE USER (reply / username)
    # =========================
    async def get_target_user(client, message):
        # Reply based
        if message.reply_to_message:
            return message.reply_to_message.from_user

        # Username / ID based
        if len(message.command) >= 2:
            try:
                return await client.get_users(message.command[1])
            except:
                return None

        return None

    # =========================
    # SET WARN LIMIT
    # =========================
    @app.on_message(filters.command("warnlimit") & filters.group)
    async def set_warn_limit(client, message):
        if not message.from_user:
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ Admins only.")

        if len(message.command) < 2 or not message.command[1].isdigit():
            return await message.reply("❗ Usage: /warnlimit <number>")

        limit = int(message.command[1])
        WARN_LIMITS[message.chat.id] = limit

        await message.reply(f"⚠️ Warn limit set to **{limit}**")

    # =========================
    # WARN USER
    # =========================
    @app.on_message(filters.command("warn") & filters.group)
    async def warn_user(client, message):
        if not message.from_user:
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply(
                "❗ Reply to a user or use:\n`/warn <username> <reason>`"
            )

        # Optional reason
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else None

        await typing(client, message.chat.id)
        count = await add_warn(message.chat.id, user.id)

        limit = WARN_LIMITS.get(message.chat.id, DEFAULT_WARN_LIMIT)

        if count >= limit:
            await client.ban_chat_member(message.chat.id, user.id)
            await reset_warn(message.chat.id, user.id)
            await message.reply(
                f"🚫 {user.mention} banned (warn limit {limit})."
            )
        else:
            text = f"⚠️ {user.mention} warned ({count}/{limit})"
            if reason:
                text += f"\n📝 Reason: {reason}"
            await message.reply(text)

    # =========================
    # REMOVE 1 WARN
    # =========================
    @app.on_message(filters.command("rmwarn") & filters.group)
    async def remove_warn(client, message):
        if not message.from_user:
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply(
                "❗ Reply to a user or use:\n`/rmwarn <username>`"
            )

        await reset_warn(message.chat.id, user.id)
        await message.reply(f"✅ Warns reset for {user.mention}")
