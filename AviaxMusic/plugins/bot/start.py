import time
import asyncio

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ChatType

import config
from AviaxMusic import app
from AviaxMusic.misc import _boot_
from AviaxMusic.utils.database import add_served_chat, add_served_user
from AviaxMusic.utils.inline import private_panel, start_panel
from AviaxMusic.utils import bot_sys_stats
from config import START_VIDEO_URL, SUPPORT_GROUP


async def send_start_video(chat_id, reply_to_message_id=None):
    """Send the start video as a quoted reply."""
    try:
        sent_video = await app.send_video(
            chat_id=chat_id,
            video=START_VIDEO_URL,
            supports_streaming=True,
            reply_to_message_id=reply_to_message_id,  # Quote the message
        )
        return sent_video
    except Exception as e:
        print(f"Error sending video: {e}")
        return None


@app.on_message(filters.command("start") & filters.private)
async def start_pm(client, message: Message):
    """Handle the /start command in private chat."""
    print(f"Received /start command from {message.from_user.mention}")

    # Log the user in the database
    await add_served_user(message.from_user.id)

    # Prepare response data
    UP, CPU, RAM, DISK = await bot_sys_stats()
    caption = (
        f"Hello {message.from_user.mention},\n\n"
        f"Welcome to the bot! Here are some stats about the system:\n"
        f"**Uptime:** {UP}\n**Disk Usage:** {DISK}\n**CPU Usage:** {CPU}\n**RAM Usage:** {RAM}\n\n"
        f"Use the buttons below to explore more!"
    )

    # Send the start video as a quoted reply
    video_message = await send_start_video(
        chat_id=message.chat.id,
        reply_to_message_id=message.message_id,
    )

    if video_message:
        print("Start video sent successfully.")
    else:
        print("Failed to send start video.")

    # Send the buttons and caption
    try:
        await app.send_message(
            chat_id=message.chat.id,
            text=caption,
            reply_markup=InlineKeyboardMarkup(private_panel(None)),
        )
        print("Start message sent successfully.")
    except Exception as e:
        print(f"Error sending start message: {e}")


@app.on_message(filters.command("start") & filters.group)
async def start_group(client, message: Message):
    """Handle the /start command in groups."""
    print(f"Received /start command in group: {message.chat.title}")

    # Log the chat in the database
    await add_served_chat(message.chat.id)

    uptime = int(time.time() - _boot_)
    caption = f"Hello, {message.chat.title}!\n\nThe bot is running smoothly.\n**Uptime:** {uptime}s."

    # Send the start video as a quoted reply
    video_message = await send_start_video(
        chat_id=message.chat.id,
        reply_to_message_id=message.message_id,
    )

    if video_message:
        print("Start video sent in group.")
    else:
        print("Failed to send start video in group.")

    # Send the caption and buttons
    try:
        await app.send_message(
            chat_id=message.chat.id,
            text=caption,
            reply_markup=InlineKeyboardMarkup(start_panel(None)),
        )
        print("Start message sent in group.")
    except Exception as e:
        print(f"Error sending start message in group: {e}")
