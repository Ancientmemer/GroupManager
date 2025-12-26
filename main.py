from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN

from database.users import save_user
from database.groups import save_group

from handlers.owner import register_owner
from handlers.admin import register_admin
from handlers.warns import register_warns
from handlers.locks import register_locks
from handlers.welcome import register_welcome
from handlers.notes import register_notes
from handlers.filters import register_filters
from handlers.start import register_start
from handlers.help import register_help


app = Client(
    "rose_clone_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# ✅ Save private users (NON-command messages only)
@app.on_message(filters.private & ~filters.command())
async def private_save(_, message):
    if message.from_user:
        await save_user(message.from_user)


# ✅ Save groups safely (NON-command, NON-service)
@app.on_message(filters.group & ~filters.command() & ~filters.service)
async def group_save(_, message):
    await save_group(message.chat)


# ✅ Register command handlers
register_start(app)
register_help(app)

register_owner(app)
register_admin(app)
register_warns(app)
register_locks(app)
register_filters(app)
register_notes(app)
register_welcome(app)


print("🤖 Bot started successfully...")
app.run()
