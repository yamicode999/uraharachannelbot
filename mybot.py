from pyrogram import Client, enums, filters
from config import (
    api_id,
    api_hash,
    bot_token,
    owner_id,
    channel_id
)

# Configuration
API_ID = api_id  
API_HASH = api_hash  
BOT_TOKEN = bot_token  
CHANNEL_ID = channel_id  
OWNER_ID = owner_id  

# List to hold admin user IDs
admins = [OWNER_ID]

# Initialize the bot
app = Client("format_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Set global parse mode to HTML
app.set_parse_mode(enums.ParseMode.HTML)

# Helper function to check if user is an admin
def is_admin(user_id):
    return user_id in admins

# Change channel command - only for owner
@app.on_message(filters.command("channel") & filters.user(OWNER_ID))
async def change_channel(client, message):
    try:
        new_channel = message.command[1]
        global CHANNEL_ID
        CHANNEL_ID = new_channel
        await message.reply(f"Channel changed to {new_channel}")
    except IndexError:
        await message.reply("Please use: /channel <channel_username or id>")

# Authorize new admin
@app.on_message(filters.command("authorize") & filters.user(OWNER_ID))
async def authorize_admin(client, message):
    try:
        user_id = int(message.command[1])
        global admins
        if user_id not in admins:
            admins.append(user_id)
            await message.reply(f"User {user_id} has been added as an admin.")
            #print(admins)
        else:
            await message.reply("This user is already an admin.")
    except (IndexError, ValueError):
        await message.reply("Please use: /authorize <telegram_user_id>")

# Revoke admin access
@app.on_message(filters.command("revoke") & filters.user(OWNER_ID))
async def revoke_admin(client, message):
    try:
        user_id = int(message.command[1])
        global admins
        if user_id in admins:
            admins.remove(user_id)
            await message.reply(f"Admin access revoked for user {user_id}.")
            #print(admins)
        else:
            await message.reply("This user is not an admin.")
    except (IndexError, ValueError):
        await message.reply("Please use: /revoke <telegram_user_id>")

# Function to process and send formatted messages
@app.on_message(filters.private)
async def send_formatted_message(client, message):
    if message.from_user.id in admins:
        if "|" in message.text:
            try:
                location, key, usable_apps = message.text.split("|", 2)
                formatted_text = (
                    f"<b>{location.strip()}</b>\n\n"
                    f"<pre><code>{key.strip()}</code></pre>\n\n"
                    f"<b>Usable in: {usable_apps.strip()}</b>"
                )
                await client.send_message(
                    chat_id=CHANNEL_ID,
                    text=formatted_text
                )
                await message.reply("Message sent successfully!")
            except ValueError:
                await message.reply("Invalid format. Use Location|Key|Usable Apps.")
        else:
            await message.reply("Please use the correct format: Location|Key|Usable Apps.")
    else:
        await message.reply("You're not authorized to use the bot.")

# Run the bot
print("Bot is running...")
app.run()