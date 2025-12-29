import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

from handlers.admin import register_admin
from handlers.filters import register_filters
from handlers.commands import register_commands
from handlers.owner import register_owner
from handlers.welcome import register_welcome


# ================== UPTIME SERVER ==================
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
# ==================================================


def main():
    app = Client(
        "GroupManager",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    # Start uptime server
    threading.Thread(target=run_http_server, daemon=True).start()

    # Register handlers
    register_admin(app)
    register_filters(app)
    register_commands(app)
    register_owner(app)
    register_welcome(app)

    print("🤖 GroupManager Bot Started")
    app.run()


if __name__ == "__main__":
    main()
