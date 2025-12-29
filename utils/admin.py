from pyrogram.enums import ChatMemberStatus

async def is_admin(client, message):
    # 1️⃣ Anonymous admin (sender_chat)
    if message.sender_chat:
        return True

    # 2️⃣ Normal admin
    if message.from_user:
        try:
            member = await client.get_chat_member(
                message.chat.id,
                message.from_user.id
            )
            return member.status in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            )
        except:
            return False

    return False
