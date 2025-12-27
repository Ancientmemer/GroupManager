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


#===================UPTIMEROBOT=====================
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()
# ========================================================

# =========================================================
# Save private users (non-command text only)
# =========================================================
@app.on_message(
    filters.private & filters.text & ~filters.regex(r"^/"),
    group=2
)
async def private_save(_, message):
    if message.from_user:
        await save_user(message.from_user)


# =========================================================
# Save groups (LOW PRIORITY – after filters)
# =========================================================
@app.on_message(
    filters.group & filters.text & ~filters.regex(r"^/") & ~filters.service,
    group=2
)
async def group_save(_, message):
    await save_group(message.chat)


# =========================================================
# Register handlers
# =========================================================
register_start(app)
register_help(app)
register_filters(app)
register_owner(app)
register_admin(app)
register_warns(app)
register_locks(app)
register_notes(app)
register_welcome(app)


print("🤖 Bot started successfully...")
app.run()
