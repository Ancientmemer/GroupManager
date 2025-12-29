from .mongodb import db

conn_col = db.connections


async def set_connection(user_id, group_id):
    await conn_col.update_one(
        {"user_id": user_id},
        {"$set": {"group_id": group_id}},
        upsert=True
    )


async def get_connection(user_id):
    return await conn_col.find_one({"user_id": user_id})


async def clear_connection(user_id):
    await conn_col.delete_one({"user_id": user_id})
