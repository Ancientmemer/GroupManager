from .mongodb import db

conn_col = db.connections


async def set_connection(user_id: int, chat_id: int):
    await conn_col.update_one(
        {"user_id": user_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )


async def get_connection(user_id: int):
    data = await conn_col.find_one({"user_id": user_id})
    return data["chat_id"] if data else None


async def clear_connection(user_id: int):
    await conn_col.delete_one({"user_id": user_id})
