from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN
from database.users import save_user
from database.groups import save_group
from handlers.owner import register_owner
from handlers.admin import register_admin

app = Client(
    "rose_clone_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.private)
async def private_save(_, message):
    await save_user(message.from_user)

@app.on_message(filters.group)
async def group_save(_, message):
    await save_group(message.chat)

register_owner(app)
register_admin(app)

app.run()
