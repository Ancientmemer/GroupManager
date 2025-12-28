from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)

# ====== CHANGE THESE ======
BOT_NAME = "Miyamizu"
UPDATES_CHANNEL = "https://t.me/jb_links"
SUPPORT_GROUP = "https://t.me/movie_maniac007"
# ==========================


def register_commands(app):

    # =========================
    # START COMMAND
    # =========================
    @app.on_message(filters.command("start"))
    async def start_cmd(client, message):

        # 🔹 Multiple images (Media Group)
        photos = [
            InputMediaPhoto("https://graph.org/file/5008f7d06e743eaa2244e-3f585d3263200f7cd0.jpg"),
            InputMediaPhoto("https://graph.org/file/6040b38cb51f5dcea0495-ceb88af1e1e97c9321.jpg"),
            InputMediaPhoto("https://graph.org/file/1a6821fcdc7fd4aae1eeb-33d7a469df2a984185.jpg")
        ]

        try:
            await client.send_media_group(
                chat_id=message.chat.id,
                media=photos
            )
        except:
            pass  # if media group fails, ignore

        text = (
            f"🤖 **Welcome to {BOT_NAME}!**\n\n"
            "I am a powerful **group management bot**.\n"
            "I help admins manage groups easily with:\n\n"
            "• ⚠️ Warn system\n"
            "• 🧠 Filters\n"
            "• 🔇 Mute / 🚫 Ban\n"
            "• 🤖 Auto replies\n\n"
            "➕ **Add me to your group and promote me as admin.**\n"
            "📖 Use /help to see all commands."
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Add me to your group",
                        url=f"https://t.me/{(await client.get_me()).username}?startgroup=true"
                    )
                ],
                [
                    InlineKeyboardButton("ℹ️ Help", callback_data="help_menu"),
                    InlineKeyboardButton("🌐 Bot Updates", url=UPDATES_CHANNEL)
                ]
            ]
        )

        await message.reply(text, reply_markup=buttons)

    # =========================
    # HELP COMMAND
    # =========================
    @app.on_message(filters.command("help"))
    async def help_cmd(client, message):
        await send_help_menu(message)

    # =========================
    # ID COMMAND
    # =========================
    @app.on_message(filters.command("id"))
    async def id_cmd(client, message):
        if message.chat.type == "private":
            await message.reply(
                f"👤 **Your User ID:** `{message.from_user.id}`"
            )
        else:
            await message.reply(
                f"👥 **Group ID:** `{message.chat.id}`"
            )

    # =========================
    # HELP MENU CALLBACK
    # =========================
    @app.on_callback_query(filters.regex("^help_menu$"))
    async def help_menu_cb(client, cb):
        await send_help_menu(cb.message, edit=True)

    # =========================
    # HELP SUB MENUS
    # =========================
    @app.on_callback_query(filters.regex("^help_"))
    async def help_sections(client, cb):
        data = cb.data

        texts = {
            "help_filters": (
                "🧠 **Filters Help**\n\n"
                "• /filter <keyword> (reply to message)\n"
                "• /filter -admin <keyword>\n"
                "• /stop <keyword>\n"
                "• /stopall\n"
                "• /filters"
            ),
            "help_warns": (
                "⚠️ **Warnings Help**\n\n"
                "• /warn <reply | user> [reason]\n"
                "• /rmwarn <reply | user>\n"
                "• /warnings <reply | user>\n"
                "• /warnlimit <number>"
            ),
            "help_admin": (
                "👮 **Admin Commands**\n\n"
                "• /ban /unban\n"
                "• /mute /unmute\n"
                "• /pin\n"
                "• /purge"
            ),
            "help_user": (
                "👤 **User Commands**\n\n"
                "• /start\n"
                "• /help\n"
                "• /id"
            ),
        }

        text = texts.get(data, "Unknown section")

        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("⬅️ Back", callback_data="help_menu")]
            ]
        )

        await cb.message.edit(text, reply_markup=buttons)

    # =========================
    # SHARED HELP MENU FUNCTION
    # =========================
    async def send_help_menu(message, edit=False):
        text = (
            f"Hey! My name is **{BOT_NAME}** 🤖\n\n"
            "I am a **group management bot**, here to help you "
            "keep order in your groups!"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🧠 Filters", callback_data="help_filters"),
                    InlineKeyboardButton("⚠️ Warnings", callback_data="help_warns")
                ],
                [
                    InlineKeyboardButton("👮 Admin Commands", callback_data="help_admin"),
                    InlineKeyboardButton("👤 User Commands", callback_data="help_user")
                ],
                [
                    InlineKeyboardButton("⬅️ Back", callback_data="help_menu")
                ]
            ]
        )

        if edit:
            await message.edit(text, reply_markup=buttons)
        else:
            await message.reply(text, reply_markup=buttons)
