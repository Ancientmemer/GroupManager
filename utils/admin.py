async def is_admin(client, message, chat_id=None):
    """
    Checks whether user is admin in a group.
    - message: original message
    - chat_id: target group id (optional)
    """

    # PM il aanenkil chat_id must be provided
    target_chat = chat_id if chat_id else message.chat.id

    # Anonymous admin (sender_chat)
    if message.sender_chat:
        return True

    if not message.from_user:
        return False

    try:
        member = await client.get_chat_member(
            target_chat,
            message.from_user.id
        )
        return member.status in ("administrator", "owner")
    except:
        return False
