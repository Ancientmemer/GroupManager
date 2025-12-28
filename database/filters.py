from database import db

# Collection name
filters_col = db.filters


# =========================
# ADD FILTER
# =========================
async def add_filter(chat_id, keyword, data):
    await filters_col.update_one(
        {"chat_id": chat_id, "keyword": keyword},
        {"$set": data},
        upsert=True
    )


# =========================
# REMOVE SINGLE FILTER
# =========================
async def remove_filter(chat_id, keyword):
    await filters_col.delete_one(
        {"chat_id": chat_id, "keyword": keyword}
    )


# =========================
# REMOVE ALL FILTERS (STOPALL)
# =========================
async def remove_all_filters(chat_id):
    await filters_col.delete_many(
        {"chat_id": chat_id}
    )


# =========================
# GET ALL FILTERS
# =========================
async def get_filters(chat_id):
    cursor = filters_col.find({"chat_id": chat_id})
    return await cursor.to_list(length=None)
