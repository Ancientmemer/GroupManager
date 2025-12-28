import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


START_IMAGES = [
    "https://telegra.ph/file/aaa111.jpg",
    "https://telegra.ph/file/bbb222.jpg",
    "https://telegra.ph/file/ccc333.jpg",
]


def register_commands(app):

    # =========================
    # /START
    # =========================
    @app.on_message(filters.command("start"))
    async def start(_, message):
        image = random.choice(START_IMAGES)

        text = (
            "🤖 **Welcome to Miyamizu!**\n\n"
            "I am a powerful **group management bot**.\n"
            "I help admins manage groups easily with:\n\n"
            "• ⚠️ Warn system\n"
            "• 🧠 Filters\n"
            "• 🔇 Mute / 🚫 Ban\n"
            "• 🤖 Auto replies\n\n"
            "➕ Add me to your group and promote me as admin.\n"
            "📖 Use /help to see all commands.\n"
            "🆔 Use /id to get user or group ID."
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Add me to your group",
                        url=f"https://t.me/{_.me.username}?startgroup=true"
                    )
                ],
                [
                    InlineKeyboardButton("ℹ️ Help", callback_data="help_menu"),
                    InlineKeyboardButton("🌐 Bot Updates", url="https://t.me/your_channel")
                ]
            ]
        )

        await message.reply_photo(
            photo=image,
            caption=text,
            reply_markup=buttons
        )

    # =========================
    # /HELP
    # =========================
    @app.on_message(filters.command("help"))
    async def help_cmd(_, message):
        await send_help_menu(message)

    async def send_help_menu(message):
        text = (
            "ℹ️ **Miyamizu Help Menu**\n\n"
            "Choose a category below to see commands."
        )

        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🧠 Filters", callback_data="help_filters")],
                [InlineKeyboardButton("⚠️ Warnings", callback_data="help_warns")],
                [InlineKeyboardButton("🛠 Admin Commands", callback_data="help_admin")],
                [InlineKeyboardButton("👤 User Commands", callback_data="help_user")],
            ]
        )

        await message.reply(text, reply_markup=buttons)

    # =========================
    # CALLBACK HANDLER
    # =========================
    @app.on_callback_query()
    async def callbacks(_, query):
        data = query.data

        if data == "help_menu":
            text = (
                "ℹ️ **Miyamizu Help Menu**\n\n"
                "Select a category:"
            )
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🧠 Filters", callback_data="help_filters")],
                    [InlineKeyboardButton("⚠️ Warnings", callback_data="help_warns")],
                    [InlineKeyboardButton("🛠 Admin Commands", callback_data="help_admin")],
                    [InlineKeyboardButton("👤 User Commands", callback_data="help_user")],
                ]
            )
            await query.message.edit_text(text, reply_markup=buttons)

        elif data == "help_filters":
            text = (
                "🧠 **Filters Commands**\n\n"
                "/filter <keyword> – Add filter (reply)\n"
                "/stop <keyword> – Remove filter\n"
                "/filters – List all filters"
            )
            await back_menu(query, text)

        elif data == "help_warns":
            text = (
                "⚠️ **Warning Commands**\n\n"
                "/warn – Warn a user\n"
                "/rmwarn – Remove one warn\n"
                "/warnings – Check warns\n"
                "/warnlimit – Set warn limit"
            )
            await back_menu(query, text)

        elif data == "help_admin":
            text = (
                "🛠 **Admin Commands**\n\n"
                "/ban / unban\n"
                "/mute / unmute\n"
                "/pin\n"
                "/purge"
            )
            await back_menu(query, text)

        elif data == "help_user":
            text = (
                "👤 **User Commands**\n\n"
                "/id – Get user / group ID\n"
                "/start – Start bot\n"
                "/help – Help menu"
            )
            await back_menu(query, text)

        await query.answer()

    async def back_menu(query, text):
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="help_menu")]]
        )
        await query.message.edit_text(text, reply_markup=buttons)

    # =========================
    # /ID
    # =========================
    @app.on_message(filters.command("id"))
    async def id_cmd(_, message):
        if message.chat.type == "private":
            await message.reply(f"🆔 **Your ID:** `{message.from_user.id}`")
        else:
            await message.reply(
                f"👥 **Group ID:** `{message.chat.id}`\n"
                f"🙋 **Your ID:** `{message.from_user.id}`"
            )
