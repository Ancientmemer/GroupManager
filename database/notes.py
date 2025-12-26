from .mongodb import db
notes = db["notes"]

async def save_note(chat_id, name, text):
    await notes.update_one(
        {"chat_id": chat_id, "name": name},
        {"$set": {"text": text}},
        upsert=True
    )

async def get_note(chat_id, name):
    data = await notes.find_one({"chat_id": chat_id, "name": name})
    return data["text"] if data else None
