from pyrogram import Client, filters
from pyrogram.types import Message

async def handle_edited_message(client: Client, message: Message):
    """
    This function handles edited messages, deletes them, and sends a message saying
    the message was edited and deleted.
    """

    # Check if the message is being edited
    if message.text and message.text != message.edit_date:  # Ensure it's an edited message
        try:
            # Delete the edited message
            await message.delete()

            # Send a message informing the user that their message was edited and deleted
            notification = f"{message.from_user.mention}, You Edited a Message And I delted it for Security Purpose."
            await message.reply(notification)
        except Exception as e:
            print(f"Error handling edited message: {e}")
