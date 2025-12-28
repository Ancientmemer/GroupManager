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
    async def is_admin(client, message):
        # Messages sent as channel (anonymous admin)
        if message.sender_chat:
            return True

        if message.from_user:
            member = await client.get_chat_member(
                message.chat.id,
                message.from_user.id
            )
            return member.status in ("administrator", "owner")

        return False

    # =========================
    # RESOLVE TARGET USER
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
    # SET WARN LIMIT
    # =========================
    @app.on_message(filters.command("warnlimit") & filters.group)
    async def set_warn_limit(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if len(message.command) < 2 or not message.command[1].isdigit():
            return await message.reply("❗ Usage: `/warnlimit <number>`")

        limit = int(message.command[1])
        WARN_LIMITS[message.chat.id] = limit

        await message.reply(f"⚠️ Warn limit set to **{limit}**")

    # =========================
    # WARN USER
    # =========================
    @app.on_message(filters.command("warn") & filters.group)
    async def warn_user(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply(
                "❗ Reply to a user or use:\n`/warn <username> <reason>`"
            )

        # ❌ Prevent warning admins
        member = await client.get_chat_member(message.chat.id, user.id)
        if member.status in ("administrator", "owner"):
            return await message.reply("❌ You can't warn admins.")

        # Parse reason safely
        reason = None
        if message.reply_to_message and len(message.command) > 1:
            reason = " ".join(message.command[1:])
        elif len(message.command) > 2:
            reason = " ".join(message.command[2:])

        await typing(client, message.chat.id, 1)

        count = await add_warn(message.chat.id, user.id)
        limit = WARN_LIMITS.get(message.chat.id, DEFAULT_WARN_LIMIT)

        # 🚫 Ban if limit reached
        if count >= limit:
            try:
                await client.ban_chat_member(message.chat.id, user.id)
                await reset_warn(message.chat.id, user.id)
                await message.reply(
                    f"🚫 {user.mention} banned (warn limit {limit})."
                )
            except Exception as e:
                await message.reply(
                    f"❌ Failed to ban {user.mention}\nError: `{e}`"
                )
        else:
            text = f"⚠️ {user.mention} warned ({count}/{limit})"
            if reason:
                text += f"\n📝 Reason: {reason}"
            await message.reply(text)

    # =========================
    # REMOVE WARN
    # =========================
    @app.on_message(filters.command("rmwarn") & filters.group)
    async def remove_warn(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply(
                "❗ Reply to a user or use:\n`/rmwarn <username>`"
            )

        await reset_warn(message.chat.id, user.id)
        await message.reply(f"✅ Warns reset for {user.mention}")
