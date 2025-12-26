from pyrogram import filters

def register_help(app):

    @app.on_message(filters.command("help"))
    async def help(_, message):
        await message.reply_text(
            "📚 **Available Commands**\n\n"
            "👮 Admin:\n"
            "/ban /mute /kick /purge\n"
            "/warn /warns\n\n"
            "🔒 Protection:\n"
            "Anti-link / Anti-spam\n\n"
            "🧠 Filters & Notes:\n"
            "/filter /stop /filters\n"
            "/save /get\n\n"
            "👑 Owner:\n"
            "/stats /broadcast"
        )
