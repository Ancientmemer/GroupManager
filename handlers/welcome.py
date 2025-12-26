from pyrogram import filters

WELCOME_TEXT = "👋 Welcome {mention} to **{chat}**!"

def register_welcome(app):

    @app.on_message(filters.new_chat_members)
    async def welcome(_, message):
        for user in message.new_chat_members:
            text = WELCOME_TEXT.format(
                mention=user.mention,
                chat=message.chat.title
            )
            await message.reply(text)

    @app.on_message(filters.left_chat_member)
    async def goodbye(_, message):
        await message.reply(f"👋 {message.left_chat_member.first_name} left.")
