import time
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup
from pyrogram.enums import ChatType

from youtubesearchpython import VideosSearch

import config
from AviaxMusic import app
from AviaxMusic.misc import _boot_
from AviaxMusic.plugins.sudo.sudoers import sudoers_list
from AviaxMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from AviaxMusic.utils import bot_sys_stats
from AviaxMusic.utils.decorators.language import LanguageStart
from AviaxMusic.utils.formatters import get_readable_time
from AviaxMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS, SUPPORT_GROUP, START_VIDEO_URL
from strings import get_string


async def send_start_video(chat_id):
    """Send the start video without a caption."""
    try:
        sent_video = await app.send_video(
            chat_id=chat_id,
            video=config.START_VIDEO_URL,
            supports_streaming=True
        )
        return sent_video
    except Exception as e:
        print(f"Error sending video: {e}")
        return None


@app.on_message(filters.command("start") & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    # Generate panels and system stats
    out = private_panel(_)
    UP, CPU, RAM, DISK = await bot_sys_stats()
    caption = _["start_2"].format(
        message.from_user.mention, app.mention, UP, DISK, CPU, RAM
    )

    # Send the video first
    video_message = await send_start_video(message.chat.id)

    if video_message:
        # Add a brief delay to ensure the video is fully sent
        await asyncio.sleep(1)

        # Send the text and inline buttons as a separate message
        try:
            await app.send_message(
                chat_id=message.chat.id,
                text=caption,
                reply_markup=InlineKeyboardMarkup(private_panel(_))
            )
        except Exception as e:
            print(f"Error sending text: {e}")

    # Log if enabled
    if await is_on_off(2):
        await app.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=f"{message.from_user.mention} started the bot."
        )


@app.on_message(filters.command("start") & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_group(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    caption = _["start_1"].format(app.mention, get_readable_time(uptime))

    # Send the video in the group
    video_message = await send_start_video(message.chat.id)

    if video_message:
        await asyncio.sleep(1)  # Ensure video is fully sent
        try:
            await app.send_message(
                chat_id=message.chat.id,
                text=caption,
                reply_markup=InlineKeyboardMarkup(out)
            )
        except Exception as e:
            print(f"Error sending text in group: {e}")

    await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                await message.chat.ban_member(member.id)

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            SUPPORT_GROUP
                        ),
                        disable_web_page_preview=True
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                caption = _["start_3"].format(
                    message.from_user.first_name,
                    app.mention,
                    message.chat.title,
                    app.mention
                )

                # Send the video for new chat members
                video_message = await send_start_video(message.chat.id)

                if video_message:
                    await asyncio.sleep(1)
                    await app.send_message(
                        chat_id=message.chat.id,
                        text=caption,
                        reply_markup=InlineKeyboardMarkup(out)
                    )
                await add_served_chat(message.chat.id)

        except Exception as ex:
            print(f"Error welcoming new members: {ex}")


# Add handler for edited messages
async def handle_edited_message(client: Client, message: Message):
    """
    This function handles edited messages, deletes them, and sends a message saying
    the message was edited and deleted.
    """
    if message.edit_date:  # Check if the message has been edited (edited message will have 'edit_date')
        try:
            # Delete the edited message
            await message.delete()

            # Send a notification message
            notification = f"Your previous message was edited and has been deleted, {message.from_user.mention}."
            await message.reply(notification)
        except Exception as e:
            print(f"Error handling edited message: {e}")


@app.on_message(filters.text)
async def edited_message_handler(client: Client, message: Message):
    # Check if the message is edited
    if message.edit_date:  # Check if the message has an edit_date (indicating it was edited)
        await handle_edited_message(client, message)
