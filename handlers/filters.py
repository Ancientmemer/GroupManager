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
from database.connections import get_connection
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
# INLINE KEYBOARD EXTRACT
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
# BUILD BUTTONS (2 PER ROW)
# =========================
def build_buttons(buttons):
    if not buttons:
        return None

    keyboard = []

    if isinstance(buttons[0], list):
        for row in buttons:
            keyboard.append([
                InlineKeyboardButton(b["text"], url=b["url"])
                for b in row
            ])
    else:
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
# HELPER: TARGET CHAT
# =========================
async def get_target_chat(client, message):
    # GROUP MODE
    if message.chat.type != "private":
        if not await is_admin(client, message):
            await message.reply("❌ Admins only.")
            return None
        return message.chat.id

    # PM MODE
    data = await get_connection(message.from_user.id)
    if not data:
        await message.reply("❗ Use `/connect <group_id>` first.")
        return None

    group_id = data["group_id"]

    if not await is_admin(client, message, chat_id=group_id):
        await message.reply("❌ You are not admin of the connected group.")
        return None

    return group_id


# =========================
# REGISTER FILTERS
# =========================
def register_filters(app):

    # =========================
    # ADD FILTER
    # =========================
    @app.on_message(filters.command("filter"))
    async def add(client, message):
        chat_id = await get_target_chat(client, message)
        if not chat_id:
            return

        if not message.reply_to_message:
            return await message.reply(
                "❗ Reply to a message with:\n"
                "`/filter word`\n"
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
            "chat_id": chat_id,
            "keyword": keyword,
            "admin_only": False,
            "buttons": []
        }

        inline_buttons = extract_inline_keyboard(reply.reply_markup)

        if reply.text:
            clean, text_buttons = extract_buttons_and_text(reply.text)
            data.update({
                "type": "text",
                "text": clean,
                "buttons": inline_buttons or text_buttons
            })

        elif reply.photo:
            clean, text_buttons = extract_buttons_and_text(reply.caption or "")
            data.update({
                "type": "photo",
                "file_id": reply.photo.file_id,
                "caption": clean,
                "buttons": inline_buttons or text_buttons
            })

        elif reply.video:
            clean, text_buttons = extract_buttons_and_text(reply.caption or "")
            data.update({
                "type": "video",
                "file_id": reply.video.file_id,
                "caption": clean,
                "buttons": inline_buttons or text_buttons
            })

        elif reply.sticker:
            data.update({
                "type": "sticker",
                "file_id": reply.sticker.file_id
            })
        else:
            return await message.reply("❌ Unsupported message type.")

        await add_filter(chat_id, keyword, data)
        await message.reply(f"✅ Filter added:\n`{keyword}`")

    # =========================
    # LIST FILTERS
    # =========================
    @app.on_message(filters.command("filters"))
    async def list_filters(client, message):
        chat_id = await get_target_chat(client, message)
        if not chat_id:
            return

        filters_list = await get_filters(chat_id)
        if not filters_list:
            return await message.reply("🧠 No active filters.")

        text = "🧠 **Active Filters**\n\n"
        for f in filters_list:
            text += f"• `{f['keyword']}`\n"

        await message.reply(text)

    # =========================
    # STOP FILTER
    # =========================
    @app.on_message(filters.command("stop"))
    async def stop(client, message):
        chat_id = await get_target_chat(client, message)
        if not chat_id:
            return

        keyword = message.text.split(maxsplit=1)[1].strip().lower()
        if keyword.startswith('"') and keyword.endswith('"'):
            keyword = keyword[1:-1]

        await remove_filter(chat_id, keyword)
        await message.reply("❌ Filter removed.")

    # =========================
    # STOP ALL
    # =========================
    @app.on_message(filters.command("stopall"))
    async def stopall(client, message):
        chat_id = await get_target_chat(client, message)
        if not chat_id:
            return

        await remove_all_filters(chat_id)
        await message.reply("🧹 All filters removed.")

    # =========================
    # WATCH (GROUP ONLY)
    # =========================
    @app.on_message(filters.group & filters.text & ~filters.command([]))
    async def watch(client, message):
        text = message.text.lower()
        filters_list = await get_filters(message.chat.id)

        for f in filters_list:
            if f["keyword"] in text:
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
