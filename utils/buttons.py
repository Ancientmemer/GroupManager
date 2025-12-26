from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def parse_buttons(text):
    """
    Format:
    [Text](buttonurl:https://example.com)
    """
    buttons = []
    for line in text.split("\n"):
        if "(buttonurl:" in line:
            label = line.split("[")[1].split("]")[0]
            url = line.split("buttonurl:")[1].split(")")[0]
            buttons.append([InlineKeyboardButton(label, url=url)])
    return InlineKeyboardMarkup(buttons) if buttons else None
