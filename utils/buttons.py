import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


BUTTON_REGEX = re.compile(
    r"\[([^\[]+)\]\(buttonurl:(.+?)\)"
)


def parse_buttons(text):
    """
    Supports:
    [Text](buttonurl:https://example.com)
    [Text](buttonurl:callback_data)
    Multiple buttons per line supported
    """

    if not text:
        return None

    keyboard = []

    for line in text.split("\n"):
        row = []

        matches = BUTTON_REGEX.findall(line)
        if not matches:
            continue

        for label, value in matches:
            # URL button
            if value.startswith("http://") or value.startswith("https://"):
                row.append(
                    InlineKeyboardButton(label, url=value)
                )
            else:
                # Callback button
                row.append(
                    InlineKeyboardButton(label, callback_data=value)
                )

        if row:
            keyboard.append(row)

    return InlineKeyboardMarkup(keyboard) if keyboard else None


def clean_button_text(text):
    """
    Removes button syntax from message text
    """
    if not text:
        return text

    return BUTTON_REGEX.sub("", text).strip()
