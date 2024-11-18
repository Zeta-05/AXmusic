import time
import asyncio

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from AviaxMusic import app
from AviaxMusic.misc import _boot_
from AviaxMusic.utils.database import add_served_chat, add_served_user, get_lang
from AviaxMusic.utils import bot_sys_stats
from AviaxMusic.utils.inline import private_panel, start_panel
from config import START_VIDEO_URL, BANNED_USERS, SUPPORT_GROUP
from strings import get_string
from AviaxMusic.utils.decorators.language import LanguageStart


async def send_start_video(chat_id, reply_to_message_id=None):
    """Send the start video as a quoted reply."""
    try:
        sent_video = await app.send_video(
            chat_id=chat_id,
            video=START_VIDEO_URL,
            supports_streaming=True,
            reply_to_message_id=reply_to_message_id,
        )
        return sent_video
    except Exception as e:
        print(f"Error sending video: {e}")
        return None


@app.on_message(filters.command("start") & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    """Handle the /start command in private chat."""
    # Log the user
    await add_served_user(message.from_user.id)

    # Retrieve system stats
    UP, CPU, RAM, DISK = await bot_sys_stats()

    # Load localized text from en.yml
    caption = _["start_2"].format(
        user_mention=message.from_user.mention,
        bot_mention=app.mention,
        uptime=UP,
        disk=DISK,
        cpu=CPU,
        ram=RAM,
    )

    # Send the start video as a quoted reply
    video_message = await send_start_video(
        chat_id=message.chat.id,
        reply_to_message_id=message.message_id,
    )

    # Send caption with buttons after the video
    if video_message:
        try:
            await app.send_message(
                chat_id=message.chat.id,
                text=caption,
                reply_markup=InlineKeyboardMarkup(private_panel(_)),
            )
        except Exception as e:
            print(f"Error sending start message: {e}")


@app.on_message(filters.command("start") & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_group(client, message: Message, _):
    """Handle the /start command in groups."""
    # Log the group
    await add_served_chat(message.chat.id)

    uptime = int(time.time() - _boot_)
    caption = _["start_1"].format(
        bot_mention=app.mention,
        uptime=f"{uptime // 3600}h {uptime % 3600 // 60}m {uptime % 60}s",
    )

    # Send the start video as a quoted reply
    video_message = await send_start_video(
        chat_id=message.chat.id,
        reply_to_message_id=message.message_id,
    )

    # Send caption with buttons after the video
    if video_message:
        try:
            await app.send_message(
                chat_id=message.chat.id,
                text=caption,
                reply_markup=InlineKeyboardMarkup(start_panel(_)),
            )
        except Exception as e:
            print(f"Error sending start message in group: {e}")
