from pyrogram import Client, enums, filters
import requests
import psutil
import random
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

# New function to get system status
def get_system_status():
    # Get CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Get memory information
    memory = psutil.virtual_memory()
    memory_total = round(memory.total / (1024.0 ** 3), 2)  # Convert to GB
    memory_used = round(memory.used / (1024.0 ** 3), 2)
    memory_percent = memory.percent

    return f"CPU Usage: {cpu_percent}%\nMemory Usage: {memory_used}/{memory_total} GB ({memory_percent}%)"

@app.on_message(filters.command("start"))
async def start(client, message):
    welcome_message = (
        "<b>Welcome to the Urahara Shop!</b>\n\n"
        "<b>✶ /key - Get random vpn key</b>\n"
        "<b>✶ /configs - Get the VPN configs</b>\n"
        "<b>✶ /sub - Get subscription link</b>\n"
        "<b>✶ /status - Check server status</b>\n"  # Added /status command
        "<b>✶ Send your vpn key here in this format.</b>\n"
        "<b>  location|key|app</b>\n\n"
        "<b>Owner Only:</b>\n"
        "<b>✶ /fetch - Fetch and save new configs</b>\n"
        "<b>✶ /channel - Change the channel where messages are sent</b>\n"
        "<b>✶ /authorize - Add new admins</b>\n"
        "<b>✶ /revoke - Remove admin access</b>\n"
    )
    await message.reply(welcome_message)

@app.on_message(filters.command("status"))
async def server_status(client, message):
    status = get_system_status()
    await message.reply(f"<pre><code>{status}</code></pre>", parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.command("start"))
async def start(client, message):
    welcome_message = (
        "<b>Welcome to the Urahara Shop!</b>\n\n"
        "<b>✶ /key - Get random vpn key</b>\n"
        "<b>✶ /configs - Get the VPN configs</b>\n"
        "<b>✶ /sub - Get subscription link</b>\n"
        "<b>✶ Send your vpn key here in this format.</b>\n"
        "<b>  location|key|app</b>\n\n"
        "<b>Owner Only:</b>\n"
        "<b>✶ /fetch - Fetch and save new configs</b>\n"
        "<b>✶ /channel - Change the channel where messages are sent</b>\n"
        "<b>✶ /authorize - Add new admins</b>\n"
        "<b>✶ /revoke - Remove admin access</b>\n"
    )
    await message.reply(welcome_message)

@app.on_message(filters.command("key"))
async def send_random_config(client, message):
    try:
        with open("configs.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            if lines:
                random_line = random.choice(lines).strip()
                await message.reply(
                    f"<pre><code>{random_line}</code></pre>",
                    parse_mode=enums.ParseMode.HTML
                    )
            else:
                await message.reply("The configs file is empty. Use /fetchconfigs to update configs.")
    except FileNotFoundError:
        await message.reply("No configs available. Please use /fetch to fetch configs first.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

@app.on_message(filters.command("sub"))
async def start(client, message):
    welcome_message = (
                    "<b>Subscription Link:</b>\n\n"
                    "<pre><code>https://github.com/yamicode999/myshittytesttt/raw/refs/heads/main/6M22D.txt</code></pre>\n\n"
                    "<b>Usable in: Hiddify, V2Box, V2rayNg, Neko Box</b>"
                )
    await message.reply(welcome_message)

# Change channel command - only for owner
@app.on_message(filters.command("channel") & filters.user(OWNER_ID))
async def change_channel(client, message):
    global CHANNEL_ID
    try:
        new_channel = message.command[1]
        # If it's a username, fetch the channel ID
        if new_channel.startswith('@'):
            chat = await client.get_chat(new_channel)
            CHANNEL_ID = chat.id
        else:
            CHANNEL_ID = int(new_channel)  # Assuming direct ID input
        await message.reply(f"Channel changed to {new_channel}")
    except IndexError:
        await message.reply("Please use: /channel <channel_username or id>")
    except ValueError:
        await message.reply("Invalid channel ID or username format.")

# Authorize new admin
@app.on_message(filters.command("authorize") & filters.user(OWNER_ID))
async def authorize_admin(client, message):
    try:
        user_id = int(message.command[1])
        global admins
        if user_id not in admins:
            admins.append(user_id)
            await message.reply(f"User {user_id} has been added as an admin.")
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
        else:
            await message.reply("This user is not an admin.")
    except (IndexError, ValueError):
        await message.reply("Please use: /revoke <telegram_user_id>")

# Fetch configs from V2ray subscription - only for owner
@app.on_message(filters.command("fetch") & filters.user(OWNER_ID))
async def fetch_configs(client, message):
    url = "https://github.com/yamicode999/myshittytesttt/raw/refs/heads/main/6M22D.txt"
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open("configs.txt", "w", encoding="utf-8") as file:  # Specify UTF-8 encoding
            file.write(response.text)
        await message.reply("Configs fetched and saved as configs.txt.")
    except requests.RequestException as e:
        await message.reply(f"Failed to fetch configs: {str(e)}")

# Send configs to any user
@app.on_message(filters.command("configs"))
async def send_configs(client, message):
    try:
        with open("configs.txt", "r", encoding="utf-8") as file:
            configs_content = file.read()
        # Use either the file name or the content, not both
        await message.reply_document(document="configs.txt")
    except FileNotFoundError:
        await message.reply("No configs available. Please use /fetchconfigs to fetch configs first.")

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
