from pyrogram import Client, enums, filters
import requests
import psutil
import random
import os
import re
import json
import base64
import socket
from config import (
    api_id,
    api_hash,
    bot_token,
    owner_id,
    channel_id,
    soto_id
)

# Directory structure
sub_folder = "sub"
configs_folder = "configs"
output_file = os.path.join(configs_folder, "allconfigs.txt")
detrojan_file = os.path.join(configs_folder, "detrojan.txt")
detrojaned_file = os.path.join(configs_folder, "detrojaned.txt")
aio_file = os.path.join(configs_folder, "aio.txt")
output_file_aio = os.path.join(configs_folder, "6M22D.txt")

github_token = "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"
github_user = "aoisora999"  # Replace with your GitHub username
github_repo = "6M22D"

# Configuration
API_ID = api_id  
API_HASH = api_hash  
BOT_TOKEN = bot_token  
CHANNEL_ID = channel_id  
OWNER_ID = owner_id  

# List to hold admin user IDs
admins = [OWNER_ID]

def get_file_content(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

def upload_file_to_github(file_name, content, branch='main'):
    url = f'https://api.github.com/repos/{github_user}/{github_repo}/contents/{file_name}'
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        "message": f"Upload {file_name}",
        "content": base64.b64encode(content).decode('utf-8'),
        "branch": branch  # Specify branch, default to 'main'
    }
    
    # Check if file already exists to get SHA if needed
    try:
        # Fetch existing file content to get SHA for updates
        existing_file = requests.get(url, headers=headers)
        if existing_file.status_code == 200:
            existing_content = json.loads(existing_file.text)
            data["sha"] = existing_content["sha"]
    except requests.RequestException as e:
        print(f"Warning: Could not fetch existing file info: {e}")

    response = requests.put(url, headers=headers, json=data)
    if response.status_code != 201 and response.status_code != 200:  # 201 for create, 200 for update
        print(f"GitHub API Response: {response.status_code}")
        print(f"Error details: {response.json()}")
    response.raise_for_status()  # Will raise an exception for bad status codes
    return response.json()

def fetch_and_process_urls():
    """
    Fetch configurations from URLs listed in text files in the 'sub' folder
    and combine them into a single file in the 'configs' folder. 

    :return: List of tuples (failed URL, error message)
    """
    os.makedirs(configs_folder, exist_ok=True)
    combined_content = []
    failed_urls = []

    if not os.path.exists(sub_folder):
        return failed_urls

    for filename in os.listdir(sub_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(sub_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    url = line.strip()
                    if url:
                        try:
                            response = requests.get(url)
                            response.raise_for_status()
                            combined_content.append(response.text)
                        except requests.RequestException as e:
                            failed_urls.append((url, str(e)))

    if combined_content:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(combined_content))
    
    return failed_urls

def remove_trojan_urls_from_file(input_file, output_file):
    """
    Remove lines containing trojan URLs from the input file and save the rest to the output file.

    Parameters:
        input_file (str): The path to the input file with potential trojan URLs.
        output_file (str): The path to the output file for cleaned lines.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
            for line in infile:
                if not line.startswith('trojan://'):
                    outfile.write(line)
        print(f"Successfully removed trojan URLs and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred while processing files: {e}")

# Function to fetch country info based on IP address
def get_country_info(ip):
    """Get country code and flag for a given IP address."""
    try:
        response = requests.get(f"https://ipwhois.app/json/{ip}")
        if response.status_code == 200:
            data = response.json()
            country_code = data.get("country_code", "")
            if country_code:
                # Unicode flag conversion from country code
                flag = chr(127462 + ord(country_code[0]) - ord('A')) + chr(127462 + ord(country_code[1]) - ord('A'))
                return f"{country_code.upper()} {flag}"
    except Exception as e:
        print(f"Error fetching country info for IP {ip}: {e}")
    return "Unknown"

# Function to resolve a domain name to an IP address
def resolve_domain_to_ip(domain):
    """Resolve a domain name to its corresponding IP address."""
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror as e:
        print(f"Error resolving domain {domain}: {e}")
    return None

# Function to process Shadowsocks URL
def process_shadowsocks_url(url):
    pattern = r"(ss://[\w-]+@)([^:]+):(\d+)(#\S+)?"
    match = re.match(pattern, url)
    if match:
        base_url = match.group(1)  # Part before the IP
        ip_or_domain = match.group(2)  # IP or domain
        port = match.group(3)  # Port

        # Determine country info
        if re.match(r"\d+\.\d+\.\d+\.\d+", ip_or_domain):
            country_info = get_country_info(ip_or_domain)
        else:
            resolved_ip = resolve_domain_to_ip(ip_or_domain)
            if resolved_ip:
                country_info = get_country_info(resolved_ip)
            else:
                country_info = "Unknown"

        return f"{base_url}{ip_or_domain}:{port}#6M22D-{country_info}"
    return url

# Function to process Shadowsocks URL
def process_shadowsocks_country(url):
    pattern = r"(ss://[\w-]+@)([^:]+):(\d+)(#\S+)?"
    match = re.match(pattern, url)
    if match:
        base_url = match.group(1)  # Part before the IP
        ip_or_domain = match.group(2)  # IP or domain
        port = match.group(3)  # Port

        # Determine country info
        if re.match(r"\d+\.\d+\.\d+\.\d+", ip_or_domain):
            country_info = get_country_info(ip_or_domain)
        else:
            resolved_ip = resolve_domain_to_ip(ip_or_domain)
            if resolved_ip:
                country_info = get_country_info(resolved_ip)
            else:
                country_info = "Unknown"

    else:
        country_info = "Unknown"
    return country_info

# Function to process Vmess URL
def process_vmess_url(vmess_url):
    try:
        base64_data = vmess_url[len("vmess://"):]
        json_data = json.loads(base64.b64decode(base64_data).decode("utf-8"))
        address = json_data.get("add", "")

        if re.match(r"\d+\.\d+\.\d+\.\d+", address):
            country_info = get_country_info(address)
        else:
            resolved_ip = resolve_domain_to_ip(address)
            if resolved_ip:
                country_info = get_country_info(resolved_ip)
            else:
                country_info = "Unknown"

        json_data["ps"] = f"6M22D-{country_info}".strip()
        updated_base64_data = base64.b64encode(json.dumps(json_data).encode("utf-8")).decode("utf-8")
        return f"vmess://{updated_base64_data}"
    except Exception as e:
        print(f"Error processing Vmess URL: {e}")
        return vmess_url

# Function to process Vmess URL
def process_vmess_country(vmess_url):
    try:
        base64_data = vmess_url[len("vmess://"):]
        json_data = json.loads(base64.b64decode(base64_data).decode("utf-8"))
        address = json_data.get("add", "")

        if re.match(r"\d+\.\d+\.\d+\.\d+", address):
            country_info = get_country_info(address)
        else:
            resolved_ip = resolve_domain_to_ip(address)
            if resolved_ip:
                country_info = get_country_info(resolved_ip)
            else:
                country_info = "Unknown"

        return country_info
    except Exception as e:
        print(f"Error processing Vmess URL: {e}")
        country_info = "Unknown"
        return country_info

# Function to process Vless URL
def process_vless_url(url):
    pattern = r"(vless://[\w-]+@[\w.-]+):(\d+)(\?\S+#)?(\S+)?"
    match = re.match(pattern, url)
    if match:
        base_url = match.group(1)
        port = match.group(2)
        query = match.group(3) or ""
        name = match.group(4) or ""
        
        ip_or_domain = re.search(r"@([\w.-]+)", base_url).group(1)
        
        if re.match(r"\d+\.\d+\.\d+\.\d+", ip_or_domain):
            country_info = get_country_info(ip_or_domain)
        else:
            resolved_ip = resolve_domain_to_ip(ip_or_domain)
            if resolved_ip:
                country_info = get_country_info(resolved_ip)
            else:
                country_info = "Unknown"

        updated_name = f"6M22D-{country_info}"
        return f"{base_url}:{port}{query}#{updated_name}"
    return url

# Function to process Vless URL
def process_vless_country(url):
    pattern = r"(vless://[\w-]+@[\w.-]+):(\d+)(\?\S+#)?(\S+)?"
    match = re.match(pattern, url)
    if match:
        base_url = match.group(1)
        port = match.group(2)
        query = match.group(3) or ""
        name = match.group(4) or ""
        
        ip_or_domain = re.search(r"@([\w.-]+)", base_url).group(1)
        
        if re.match(r"\d+\.\d+\.\d+\.\d+", ip_or_domain):
            country_info = get_country_info(ip_or_domain)
        else:
            resolved_ip = resolve_domain_to_ip(ip_or_domain)
            if resolved_ip:
                country_info = get_country_info(resolved_ip)
            else:
                country_info = "Unknown"
    else:
        country_info = "Unknown"
    return country_info

# Function to process hy2 URL
def process_hy2_url(url):
    pattern = r"(hy2://[^?]+)\??(.*)"
    match = re.match(pattern, url)
    if match:
        base_url = match.group(1)
        query_params = match.group(2)
        domain_or_ip_match = re.search(r'@([^:]+):', base_url)
        
        if domain_or_ip_match:
            domain_or_ip = domain_or_ip_match.group(1)
            
            if re.match(r"\d+\.\d+\.\d+\.\d+", domain_or_ip):
                country_info = get_country_info(domain_or_ip)
            else:
                resolved_ip = resolve_domain_to_ip(domain_or_ip)
                if resolved_ip:
                    country_info = get_country_info(resolved_ip)
                else:
                    country_info = "Unknown"

            if '#' in query_params:
                query_params = re.sub(r'#.*', f'#6M22D-{country_info}', query_params)
            else:
                query_params += f'#6M22D-{country_info}'

            return f"{base_url}?{query_params}"
    
    return url

# Function to process hy2 URL
def process_hy2_country(url):
    pattern = r"(hy2://[^?]+)\??(.*)"
    match = re.match(pattern, url)
    if match:
        base_url = match.group(1)
        query_params = match.group(2)
        domain_or_ip_match = re.search(r'@([^:]+):', base_url)
        
        if domain_or_ip_match:
            domain_or_ip = domain_or_ip_match.group(1)
            
            if re.match(r"\d+\.\d+\.\d+\.\d+", domain_or_ip):
                country_info = get_country_info(domain_or_ip)
            else:
                resolved_ip = resolve_domain_to_ip(domain_or_ip)
                if resolved_ip:
                    country_info = get_country_info(resolved_ip)
                else:
                    country_info = "Unknown"
        else:
            country_info = "Unknown"
    else:
        country_info = "Unknown"

    return country_info

# Process a single file and return the updated lines
def process_file(file_path):
    updated_lines = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                if line.startswith("ss://"):
                    updated_lines.append(process_shadowsocks_url(line))
                elif line.startswith("vmess://"):
                    updated_lines.append(process_vmess_url(line))
                elif line.startswith("vless://"):
                    updated_lines.append(process_vless_url(line))
                elif line.startswith("hy2://"):
                    updated_lines.append(process_hy2_url(line))
                else:
                    updated_lines.append(line)  # If URL type is unknown, keep it unchanged
    return updated_lines

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

# Helper function to check if user is an admin
def is_admin(user_id):
    return user_id in admins

# Initialize the bot
app = Client("format_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Set global parse mode to HTML
app.set_parse_mode(enums.ParseMode.HTML)

@app.on_message(filters.command("start"))
async def start(client, message):
    welcome_message = (
        "<b>Welcome to the Urahara Shop!</b>\n\n"
        "<b>✶ /key - Get random vpn key</b>\n"
        "<b>✶ /sub - Get subscription link</b>\n"
        "<b>✶ /app - Download Usable Apps</b>\n\n"
        "<b>Owner Only:</b>\n"
        "<b>✶ /cmd - Get all commands</b>\n"
        "<b>✶ @onepass_api - Contact Owner</b>\n\n"
        "<b>:VPN Keys are updated daily.</b>\n"
        "<b>:You can share your vpn key,</b>\n"
        "<b> Just by sending to the bot!</b>\n"
    )
    await message.reply(welcome_message)

@app.on_message(filters.command("app"))
async def start(client, message):
    welcome_message = (
        "<b>FOR PC:</b>\n"
        '<b>✶ <a href="https://github.com/hiddify/hiddify-app/releases/latest/download/Hiddify-Windows-Setup-x64.Msix">Hiddify</a></b>\n\n'
        "<b>FOR IOS:</b>\n"
        '<b>✶ <a href="https://apps.apple.com/us/app/hiddify-proxy-vpn/id6596777532?platform=iphone">Hiddify</a></b>\n'
        '<b>✶ <a href="https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690">V2BOx</a></b>\n'
        '<b>✶ <a href="https://apps.apple.com/us/app/potatso/id1239860606">Potatso</a></b>\n\n'
        "<b>FOR ANDROID:</b>\n"
        '<b>✶ <a href="https://play.google.com/store/apps/details?id=app.hiddify.com">Hiddify</a></b>\n'
        '<b>✶ <a href="https://play.google.com/store/apps/details?id=com.v2ray.ang">V2rayNG</a></b>\n'
        '<b>✶ <a href="https://github.com/MatsuriDayo/NekoBoxForAndroid/releases/download/1.3.4/NB4A-1.3.4-armeabi-v7a.apk">Neko Box</a></b>\n'
        '<b>✶ <a href="https://play.google.com/store/apps/details?id=com.github.shadowsocks">Shadowsocks</a></b>\n'
    )
    await message.reply(welcome_message, disable_web_page_preview=True)

@app.on_message(filters.command("cmd"))
async def start(client, message):
    if message.from_user.id == owner_id:
        welcome_message = (
            "<b>Owner Commands:</b>\n\n"
            "<b>✶ /status - Check server status</b>\n"
            "<b>✶ /fetch - Fetch and save new configs</b>\n"
            "<b>✶ /fetchall - Fetch and save raw configs</b>\n"
            "<b>✶ /channel - Change the channel where messages are sent</b>\n"
            "<b>✶ /authorize - Add new admins</b>\n"
            "<b>✶ /revoke - Remove admin access</b>\n"
            "<b>✶ send detrojan.txt - Remove trojan urls</b>\n"
            "<b>✶ send aio.txt - Change Name and server</b>\n"
            "<b>✶ send 6M22D.txt - Upload to github</b>\n"
            "<b>✶ send post.txt - Post on channel</b>\n"
        )
        await message.reply(welcome_message)
    else:
        await message.reply("<b>You are not authorized to use this command.</b>")

@app.on_message(filters.command("status"))
async def server_status(client, message):
    status = get_system_status()
    await message.reply(f"<pre><code>{status}</code></pre>", parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.command("fetchall") & filters.user(OWNER_ID))
async def fetch_all_configs(client, message):
    failed_urls = fetch_and_process_urls()
    if os.path.exists(output_file):
        await client.send_document(chat_id=OWNER_ID, document=output_file)
        os.remove(output_file)  # Delete the file after sending
        if failed_urls:
            fail_msg = "\n".join([f"- {url}: {error}" for url, error in failed_urls])
            await message.reply(f"All configs fetched. Some URLs failed:\n\n{fail_msg}")
        else:
            await message.reply("<b>All configs fetched successfully.</b>")
    else:
        await message.reply("<b>No configs were fetched or no sub.txt file was provided.</b>")

@app.on_message(filters.command("sub"))
async def start(client, message):
    welcome_message = (
                    "<b>Subscription Link:</b>\n\n"
                    "<pre><code>https://github.com/aoisora999/6M22D/raw/refs/heads/main/6M22D.txt</code></pre>\n\n"
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
        await message.reply(f"<b>Channel changed to {new_channel}.</b>")
    except IndexError:
        await message.reply("<b>Please use: /channel <channel_username or id></b>")
    except ValueError:
        await message.reply("<b>Invalid channel ID or username format.</b>")

# Authorize new admin
@app.on_message(filters.command("authorize") & filters.user(OWNER_ID))
async def authorize_admin(client, message):
    try:
        user_id = int(message.command[1])
        global admins
        if user_id not in admins:
            admins.append(user_id)
            await message.reply(f"<b>User {user_id} has been added as an admin.</b>")
        else:
            await message.reply("<b>This user is already an admin.</b>")
    except (IndexError, ValueError):
        await message.reply("<b>Please use: /authorize <telegram_user_id></b>")

# Revoke admin access
@app.on_message(filters.command("revoke") & filters.user(OWNER_ID))
async def revoke_admin(client, message):
    try:
        user_id = int(message.command[1])
        global admins
        if user_id in admins:
            admins.remove(user_id)
            await message.reply(f"<b>Admin access revoked for user {user_id}.</b>")
        else:
            await message.reply("<b>This user is not an admin.</b>")
    except (IndexError, ValueError):
        await message.reply("<b>Please use: /revoke <telegram_user_id></b>")

@app.on_message(filters.command("fetch") & filters.user(OWNER_ID))
async def fetch_configs(client, message):
    url = "https://github.com/aoisora999/6M22D/raw/refs/heads/main/6M22D.txt"
    try:
        response = requests.get(url)
        response.raise_for_status()
        configs = response.text.splitlines()
        
        # Dictionary to hold configurations
        config_dict = {}
        
        for config in configs:
            config_url = config.strip()
            if config_url:
                # Determine apps where the config is usable
                if config_url.startswith("ss://"):
                    usable_apps = "Hiddify, Potatso, Neko Box, Shadowsocks"
                    country_info = process_shadowsocks_country(config_url)

                elif config_url.startswith("vmess://"):
                    usable_apps = "Hiddify, V2Box, V2rayNG, Neko Box"
                    country_info = process_vmess_country(config_url)

                elif config_url.startswith("vless://"):
                    usable_apps = "Hiddify, V2Box, V2rayNG, Neko Box"
                    country_info = process_vless_country(config_url)

                elif config_url.startswith("hy2://"):
                    usable_apps = "Hiddify, Neko Box"
                    country_info = process_hy2_country(config_url)

                else:
                    usable_apps = "Unknown"
                    country_info = "Unknown"
                
                config_dict[config_url] = {
                    "server_location": country_info,
                    "config_url": config_url,
                    "usable_apps": usable_apps
                }

        # Save as JSON file (lightweight on CPU for writing operations)
        with open("configs.json", "w", encoding="utf-8") as json_file:
            json.dump(config_dict, json_file, ensure_ascii=False, indent=2)
        
        await message.reply("<b>Configs fetched and saved as configs.json.</b>")
    except requests.RequestException as e:
        await message.reply(f"<b>Failed to fetch configs: {str(e)}</b>")

@app.on_message(filters.document & filters.user(OWNER_ID))
async def handle_sub_file(client, message):
    if message.document.file_name == 'sub.txt':
        await client.download_media(message, file_name=os.path.join(sub_folder, 'sub.txt'))
        await message.reply("Sub.txt file saved.")

    elif message.document.file_name == 'detrojan.txt':
        await client.download_media(message, file_name=detrojan_file)
        
        # Process the file to remove trojan URLs
        remove_trojan_urls_from_file(detrojan_file, detrojaned_file)
        
        # Send back the cleaned file
        await client.send_document(chat_id=OWNER_ID, document=detrojaned_file)
        
        # Delete temporary files
        for file_path in [detrojan_file, detrojaned_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        
        await message.reply("<b>Trojan URLs have been removed and the cleaned file has been sent back.</b>")

    elif message.document.file_name == 'aio.txt':
        # Save the uploaded file
        await client.download_media(message, file_name=aio_file)
        
        # Process the file
        updated_lines = process_file(aio_file)
        
        # Write the processed lines to the output file
        with open(output_file_aio, "w", encoding="utf-8") as out_file:
            out_file.write("\n".join(updated_lines))

        # Send back the processed file
        await client.send_document(chat_id=OWNER_ID, document=output_file_aio)
        
        # Delete temporary files
        for file_path in [aio_file, output_file_aio]:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        
        await message.reply("<b>Processing completed and the output file has been sent back.</b>")

    elif message.document.file_name == '6M22D.txt':
        # Download the file to a predefined path
        local_file_path = os.path.join(os.getcwd(), '6M22D.txt')  # Using current working directory
        await client.download_media(message, file_name=local_file_path)
        
        try:
            # Check if the file was actually downloaded
            if not os.path.exists(local_file_path):
                raise FileNotFoundError(f"File not found at {local_file_path}")

            # Read the content of the file
            file_content = get_file_content(local_file_path)
            
            # Upload to GitHub
            github_response = upload_file_to_github('6M22D.txt', file_content)
            print(f"File uploaded to GitHub: {github_response}")
            
            # Delete the local file after upload
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                print(f"File {local_file_path} deleted successfully.")
            
            await message.reply("<b>6M22D.txt uploaded to GitHub and local file deleted.</b>")
        except FileNotFoundError as e:
            await message.reply(f"<b>File not found: {str(e)}</b>")
        except Exception as e:
            await message.reply(f"<b>An error occurred while uploading to GitHub: {str(e)}</b>")
            print(f"Error uploading file: {e}")

    elif message.document.file_name == "post.txt":
        try:
            file_path = await client.download_media(message.document)

            # Read the content of the file
            with open(file_path, "r", encoding="utf-8") as file:
                configs = file.read().splitlines()

            # Process and send each config to the channel
            for config in configs:
                config_url = config.strip()
                if config_url:
                    # Determine apps where the config is usable and fetch country info
                    if config_url.startswith("ss://"):
                        usable_apps = "Hiddify, Potatso, Neko Box, Shadowsocks"
                        country_info = process_shadowsocks_country(config_url)

                    elif config_url.startswith("vmess://"):
                        usable_apps = "Hiddify, V2Box, V2rayNG, Neko Box"
                        country_info = process_vmess_country(config_url)

                    elif config_url.startswith("vless://"):
                        usable_apps = "Hiddify, V2Box, V2rayNG, Neko Box"
                        country_info = process_vless_country(config_url)

                    elif config_url.startswith("hy2://"):
                        usable_apps = "Hiddify, Neko Box"
                        country_info = process_hy2_country(config_url)

                    else:
                        usable_apps = "Unknown"
                        country_info = "Unknown"
                    
                    formatted_text = (
                        f"<b>{country_info.strip()}</b>\n\n"
                        f"<pre><code>{config_url.strip()}</code></pre>\n\n"
                        f"<b>Usable in: {usable_apps.strip()}</b>"
                    )
                    await client.send_message(
                        chat_id=CHANNEL_ID,  # Replace with your channel's username or ID
                        text=formatted_text,
                        parse_mode=enums.ParseMode.HTML
                    )

            # Inform the user that posting was successful
            await message.reply("<b>Configs have been posted to the channel.</b>")
            
            # Clean up: remove the downloaded file
            import os
            os.remove(file_path)

        except Exception as e:
            await message.reply(f"<b>An error occurred: {str(e)}</b>")

    else:
        pass

@app.on_message(filters.command("key"))
async def send_random_config(client, message):
    try:
        with open("configs.json", "r", encoding="utf-8") as file:
            configs = json.load(file)
            if configs:
                # Choose random config
                random_config = random.choice(list(configs.items()))
                config_url, details = random_config
                
                # Format the message
                formatted_text = (
                    f"<b>{details['server_location'].strip()}</b>\n\n"
                    f"<pre><code>{config_url.strip()}</code></pre>\n\n"
                    f"<b>Usable in: {details['usable_apps'].strip()}</b>"
                )
                await message.reply(
                    formatted_text,
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await message.reply("<b>The configs file is empty.</b>")
    except FileNotFoundError:
        await message.reply("<b>VPN Key is not available rn.</b>")
    except json.JSONDecodeError:
        await message.reply("<b>Error decoding JSON in configs.json.</b>")
    except Exception as e:
        await message.reply(f"<b>An error occurred: {str(e)}</b>")

# Function to process and send formatted messages
@app.on_message(filters.private)
async def send_formatted_message(client, message):
    if message.from_user.id in admins:
        if message.text is not None:
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
                    await message.reply("<b>Message sent successfully!</b>")
                except ValueError:
                    await message.reply("<b>Invalid format. Use Location|Key|Usable Apps.</b>")
            else:
                await message.reply("<b>Please use the correct format: Location|Key|Usable Apps.</b>")
    else:
        if message.text is not None:
            message_text = message.text.strip()
            if message_text.startswith(("vmess://", "vless://", "ss://", "hy2://")):
                if message_text.startswith("ss://"):
                    usable_apps = "Hiddify, Potatso, Neko Box, Shadowsocks"
                    country_info = process_shadowsocks_country(message_text)
                        
                elif message_text.startswith("vmess://"):
                    usable_apps = "Hiddify, V2Box, V2rayNG, Neko Box"
                    country_info = process_vmess_country(message_text)

                elif message_text.startswith("vless://"):
                    usable_apps = "Hiddify, V2Box, V2rayNG, Neko Box"
                    country_info = process_vless_country(message_text)
                        
                elif message_text.startswith("hy2://"):
                    usable_apps = "Hiddify, Neko Box"
                    country_info = process_hy2_country(message_text)
                        
                else:
                    usable_apps = "Unknown"
                    country_info = "Unknown"
                
                # Format the message
                formatted_text = (
                    f"<b>{country_info.strip()}</b>\n\n"
                    f"<pre><code>{message_text}</code></pre>\n\n"
                    f"<b>Usable in: {usable_apps}</b>"
                )
                await client.send_message(
                    chat_id=soto_id,
                    text=formatted_text
                )
                await message.reply("<b>Thank you for sharing your key!</b>")
            else:
                await message.reply("<b>Please only send VMess, VLess, Shadowsocks or Hysteria key.</b>")

# Run the bot
print("Bot is running...")
app.run()
