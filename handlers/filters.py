from pyrogram import filters
from utils.admin import is_admin
from utils.typing import typing
from utils.buttons import parse_buttons
from database.filters import (
    add_filter,
    remove_filter,
    remove_all_filters,
    get_filters
)


def register_filters(app):

    # =========================
    # ADD FILTER (ADMIN ONLY)
    # =========================
    @app.on_message(filters.command("filter") & filters.group)
    async def add_filter_handler(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if len(message.command) < 2:
            return await message.reply(
                "❗ Usage:\nReply to a message with:\n`/filter <keyword>`"
            )

        if not message.reply_to_message:
            return await message.reply(
                "❗ Reply to a message (text / media) with:\n`/filter <keyword>`"
            )

        keyword = message.command[1].lower()
        reply = message.reply_to_message

        data = {
            "chat_id": message.chat.id,
            "keyword": keyword,
            "type": None,
            "text": None,
            "file_id": None,
            "caption": None,
            "buttons": None
        }

        # TEXT
        if reply.text:
            data["type"] = "text"
            data["text"] = reply.text
            data["buttons"] = parse_buttons(reply.text)

        # PHOTO
        elif reply.photo:
            data["type"] = "photo"
            data["file_id"] = reply.photo.file_id
            data["caption"] = reply.caption
            data["buttons"] = parse_buttons(reply.caption or "")

        # VIDEO
        elif reply.video:
            data["type"] = "video"
            data["file_id"] = reply.video.file_id
            data["caption"] = reply.caption
            data["buttons"] = parse_buttons(reply.caption or "")

        # STICKER
        elif reply.sticker:
            data["type"] = "sticker"
            data["file_id"] = reply.sticker.file_id

        # GIF / ANIMATION
        elif reply.animation:
            data["type"] = "animation"
            data["file_id"] = reply.animation.file_id
            data["caption"] = reply.caption
            data["buttons"] = parse_buttons(reply.caption or "")

        else:
            return await message.reply("❌ Unsupported message type.")

        await add_filter(message.chat.id, keyword, data)
        await message.reply(f"✅ Filter `{keyword}` added successfully!")

    # =========================
    # REMOVE SINGLE FILTER
    # =========================
    @app.on_message(filters.command(["stop", "stopfilter"]) & filters.group)
    async def stop_filter_handler(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if len(message.command) < 2:
            return await message.reply("❗ Usage: `/stop <keyword>`")

        keyword = message.command[1].lower()
        await remove_filter(message.chat.id, keyword)
        await message.reply(f"❌ Filter `{keyword}` removed.")

    # =========================
    # STOP ALL FILTERS
    # =========================
    @app.on_message(filters.command("stopall") & filters.group)
    async def stop_all_filters_handler(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        await remove_all_filters(message.chat.id)
        await message.reply("🗑️ All filters removed from this group.")

    # =========================
    # LIST FILTERS
    # =========================
    @app.on_message(filters.command("filters") & filters.group)
    async def list_filters_handler(client, message):
        filters_list = await get_filters(message.chat.id)

        if not filters_list:
            return await message.reply("🧠 No active filters in this group.")

        text = "🧠 **Active Filters**\n\n"
        for f in filters_list:
            text += f"• `{f['keyword']}`\n"

        await message.reply(text)

    # =========================
    # AUTO FILTER REPLY
    # =========================
    @app.on_message(
        filters.group & (filters.text | filters.caption) & ~filters.regex(r"^/"),
        group=10
    )
    async def auto_filter_reply(client, message):
        text = message.text or message.caption
        if not text:
            return

        words = text.lower().split()
        filters_list = await get_filters(message.chat.id)
        if not filters_list:
            return

        for f in filters_list:
            if f["keyword"] in words:
                await typing(client, message.chat.id, 1)

                if f["type"] == "text":
                    await message.reply(
                        f["text"],
                        reply_markup=f.get("buttons"),
                        quote=True
                    )

                elif f["type"] == "photo":
                    await message.reply_photo(
                        f["file_id"],
                        caption=f.get("caption"),
                        reply_markup=f.get("buttons"),
                        quote=True
                    )

                elif f["type"] == "video":
                    await message.reply_video(
                        f["file_id"],
                        caption=f.get("caption"),
                        reply_markup=f.get("buttons"),
                        quote=True
                    )

                elif f["type"] == "sticker":
                    await message.reply_sticker(f["file_id"], quote=True)

                elif f["type"] == "animation":
                    await message.reply_animation(
                        f["file_id"],
                        caption=f.get("caption"),
                        reply_markup=f.get("buttons"),
                        quote=True
                    )

                break
