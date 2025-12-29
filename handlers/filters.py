from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.admin import is_admin
from utils.typing import typing
from database.filters import (
    add_filter,
    remove_filter,
    remove_all_filters,
    get_filters
)
import re


# =========================
# TEXT BUTTON PARSER
# =========================
def extract_buttons_and_text(text: str):
    buttons = []

    def repl(match):
        buttons.append({
            "text": match.group(1),
            "url": match.group(2)
        })
        return ""

    clean_text = re.sub(
        r"\[([^\]]+)\]\(buttonurl:([^)]+)\)",
        repl,
        text or ""
    ).strip()

    return clean_text, buttons


# =========================
# INLINE KEYBOARD → DB FORMAT
# (FORWARDED MESSAGES)
# =========================
def extract_inline_keyboard(reply_markup):
    if not reply_markup or not reply_markup.inline_keyboard:
        return []

    keyboard = []
    for row in reply_markup.inline_keyboard:
        btn_row = []
        for btn in row:
            if btn.url:
                btn_row.append({
                    "text": btn.text,
                    "url": btn.url
                })
        if btn_row:
            keyboard.append(btn_row)

    return keyboard


# =========================
# BUILD INLINE BUTTONS
# ✅ 2 BUTTONS PER ROW
# =========================
def build_buttons(buttons):
    if not buttons:
        return None

    keyboard = []

    # Case 1: already row-based (forwarded inline buttons)
    if isinstance(buttons[0], list):
        for row in buttons:
            keyboard.append([
                InlineKeyboardButton(b["text"], url=b["url"])
                for b in row
            ])
    else:
        # Case 2: flat list → make 2 buttons per row
        row = []
        for btn in buttons:
            row.append(
                InlineKeyboardButton(btn["text"], url=btn["url"])
            )
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


# =========================
# REGISTER FILTERS
# =========================
def register_filters(app):

    # =========================
    # ADD FILTER
    # =========================
    @app.on_message(filters.command("filter") & filters.group)
    async def add(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply(
                "❗ Reply to a message with:\n"
                "`/filter <word>`\n"
                "`/filter \"full sentence\"`"
            )

        raw = message.text.split(maxsplit=1)
        if len(raw) < 2:
            return await message.reply("❗ Usage: /filter <keyword>")

        keyword = raw[1].strip()
        if keyword.startswith('"') and keyword.endswith('"'):
            keyword = keyword[1:-1]

        keyword = keyword.lower()
        reply = message.reply_to_message

        data = {
            "chat_id": message.chat.id,
            "keyword": keyword,
            "admin_only": False,
            "buttons": []
        }

        # 🔥 Priority: forwarded inline buttons
        inline_buttons = extract_inline_keyboard(reply.reply_markup)

        # ================= TEXT =================
        if reply.text:
            clean, text_buttons = extract_buttons_and_text(reply.text)
            data.update({
                "type": "text",
                "text": clean,
                "buttons": inline_buttons if inline_buttons else text_buttons
            })

        # ================= PHOTO =================
        elif reply.photo:
            caption = reply.caption or ""
            clean, text_buttons = extract_buttons_and_text(caption)
            data.update({
                "type": "photo",
                "file_id": reply.photo.file_id,
                "caption": clean,
                "buttons": inline_buttons if inline_buttons else text_buttons
            })

        # ================= VIDEO =================
        elif reply.video:
            caption = reply.caption or ""
            clean, text_buttons = extract_buttons_and_text(caption)
            data.update({
                "type": "video",
                "file_id": reply.video.file_id,
                "caption": clean,
                "buttons": inline_buttons if inline_buttons else text_buttons
            })

        # ================= STICKER =================
        elif reply.sticker:
            data.update({
                "type": "sticker",
                "file_id": reply.sticker.file_id
            })

        else:
            return await message.reply("❌ Unsupported message type.")

        await add_filter(message.chat.id, keyword, data)
        await message.reply(f"✅ Filter added for:\n`{keyword}`")

    # =========================
    # REMOVE FILTER
    # =========================
    @app.on_message(filters.command("stop") & filters.group)
    async def stop(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        keyword = message.text.split(maxsplit=1)[1].strip().lower()
        if keyword.startswith('"') and keyword.endswith('"'):
            keyword = keyword[1:-1]

        await remove_filter(message.chat.id, keyword)
        await message.reply("❌ Filter removed.")

    # =========================
    # STOP ALL
    # =========================
    @app.on_message(filters.command("stopall") & filters.group)
    async def stopall(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        await remove_all_filters(message.chat.id)
        await message.reply("🧹 All filters removed.")

    # =========================
    # LIST FILTERS
    # =========================
    @app.on_message(filters.command("filters") & filters.group)
    async def list_filters(client, message):
        filters_list = await get_filters(message.chat.id)
        if not filters_list:
            return await message.reply("🧠 No active filters.")

        text = "🧠 **Active Filters**\n\n"
        for f in filters_list:
            text += f"• `{f['keyword']}`\n"

        await message.reply(text)

    # =========================
    # WATCH MESSAGES
    # =========================
    @app.on_message(filters.group & filters.text & ~filters.command([]))
    async def watch(client, message):
        text = message.text.lower()
        filters_list = await get_filters(message.chat.id)

        for f in filters_list:
            if f["keyword"] in text:

                if f.get("admin_only") and not await is_admin(client, message):
                    continue

                await typing(client, message.chat.id, 1)
                markup = build_buttons(f.get("buttons"))

                if f["type"] == "text":
                    await message.reply(f["text"], reply_markup=markup)

                elif f["type"] == "photo":
                    await message.reply_photo(
                        f["file_id"],
                        caption=f.get("caption"),
                        reply_markup=markup
                    )

                elif f["type"] == "video":
                    await message.reply_video(
                        f["file_id"],
                        caption=f.get("caption"),
                        reply_markup=markup
                    )

                elif f["type"] == "sticker":
                    await message.reply_sticker(f["file_id"])

                break
