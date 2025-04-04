# import yt_dlp
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyrogram import Client, filters, idle  # Pyrogram for Telegram bot functionality
import logging  # For logging messages
import asyncio  # For asynchronous programming
import os  # For operating system dependent functionality (like file handling)
import subprocess  # For running shell commands
import json  # For handling JSON data
from pyrogram.errors import ChatAdminRequired
import time  # For time-related functions
import shlex  # For splitting shell commands
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton  # For Telegram message types and buttons
from typing import Tuple  # For type hinting
from datetime import datetime, timedelta  # For date and time manipulation
from os.path import join, exists  # For file path operations
from hachoir.metadata import extractMetadata  # For extracting metadata from files
from hachoir.parser import createParser  # For parsing files
from config import Config  # For configuration settings (like API keys)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO)

_LOG = logging.getLogger(__name__)

mbot = Client(
    "mpaidbot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
   # max_concurrent_transmissions=10000
)

# Check if Streamlink is installed
try:
    import streamlink
    _LOG.info("Streamlink is installed.")
except ImportError:
    raise ImportError("Streamlink is not installed. Please install it using 'pip install streamlink'.")

# Command for streamlink (assuming it is installed globally or needs to be manually set up)
STREAMLINK_PATH = "streamlink"  # You can modify this if Streamlink isn't globally installed



# Telegram max message length
MAX_MESSAGE_LENGTH = 4096

# Handle logging requests for the bot owner
@mbot.on_message(filters.command(["log", "logs"]) & filters.user(Config.OWNER_ID))
async def get_log_wm(bot, message) -> None:
    try:
        await message.reply_document("log.txt")
    except Exception as e:
        _LOG.info(e)

# Handle displaying available channels for authorized users
# @mbot.on_message(filters.command(["channels"]) & filters.user(Config.AUTH_USERS))
# async def show_channels_handler(bot, message) -> None:
#    getChannels(bot, message)

# ✅ Command: /start
@mbot.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_photo(
        photo="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj8JPkKsJeIJbvJQiCfXFSSXXqc33vjYgHZbJL7R6_ig4gTBXGRnjpnGO_fijlcnIxh_L3BrWu361S2dZTtHKMPkqnMH961KjwkcK9MjUewj2xHV9EX7X_yeywUcmsL2wbAxoLrZY1RQ_5wpOYARYvMhiYCY59axTPOkpiNeMWpCW0vvtYsG-znR4oOqc7q/s1600/IMG_20250317_192445_857.jpg",
        caption=(
            "<b>✨ Welcome to M3u8-DL Bot!</b>\n\n"
            "🚀 Send any link with /jl command to record it!\n"
            "<code>Coded By SharkToonsIndia and Owned by Mr. X</code>"
        )
    )

@mbot.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = (
        "<b>Available Commands:</b>\n\n"
        "<code>/start - </code><i> Start the bot and receive a welcome message.\n</i>"
        "<code>/jl link duration channel title - </code><i> Record a live link.\n</i>"
        "   - Example: <code><i>/jl https://example.com/live-link.m3u8 00:05:00 my_channel my_title</code>\n</i>"
        "<code>/help - </code><i>Show this help message.\n</i>"
        "<code>/log - </code><i>Get the log file (for owner only).\n</i>"
        "<code>Reply to a message with /quote - </code><i>Quote a message.\n\n</i>"
        "<b>Note:</b> <code>Make sure you have the necessary permissions to use certain commands.</code>"
    )
    
    await message.reply(help_text)

@mbot.on_message(filters.private)  # Only respond to private messages
async def handle_private_message(client, message):
    user_id = message.from_user.id  # Get the user ID of the sender

    # Check if the user is authorized
    if user_id not in Config.PM_AUTH_USERS:
        # Send a message if the user is not authorized
        await message.reply(
            "<code>Hey Dude, seems like master hasn't given you access to use me.\n"
            "Please contact him immediately</code>",
        )
        return  # Exit the function if the user is not authorized

    # Authorized users can use the bot normally
    # Check if the message is a command
    if message.text.startswith("/"):
        # If the command is /jl, handle it
        if message.text.startswith("/jl"):
            await main_func(client, message)  # Call the main_func to handle the /jl command
            return

@mbot.on_message(filters.group)  # Only respond to group messages
async def handle_group_message(client: Client, message) -> None:
    user_id = message.from_user.id  # Get the user ID of the sender
    username = message.from_user.username if message.from_user.username else "N/A"  # Get the username, if available
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current time

    # Check if the message is from a specific group
    if message.chat.id != Config.CHAT_ID:
        # Check if the message is a specific command
        unauthorized_commands = ["/jl", "/settings", "/another_command", "/yet_another_command"]
        if any(message.text.startswith(cmd) for cmd in unauthorized_commands):
            await message.reply(
                "<code>This bot is not authorized to respond in this group. Contact Support now.</code>"
            )
            
            try:
                await client.send_message(
                    chat_id=Config.OWNER_ID,
                    text=(
                        "<i>Unauthorized group has accessed your bot and its commands, here are its full details:</i>\n\n"
                        f"<b>Group Name:</b> <code>{message.chat.title}</code>\n"
                        f"<b>Group ID:</b> <code>{message.chat.id}</code>\n"
                        f"<b>User:</b> <code>{message.from_user.first_name} {message.from_user.last_name if message.from_user.last_name else ''}</code>\n"
                        f"<b>Username:</b> <code>@{username}</code>\n"
                        f"<b>User ID:</b> <code>{user_id}</code>\n"
                        f"<b>Language Code:</b> <code>{message.from_user.language_code if message.from_user.language_code else 'N/A'}</code>\n"
                        f"<b>Message Type:</b> <code>{message.chat.type}</code>\n"
                        f"<b>Command / Message:</b> <code>{message.text}</code>\n"
                        f"<b>Message ID:</b> <code>{message.id}</code>\n"
                        f"<b>User Profile Photo:</b> <code>{message.from_user.photo.small_file_id if message.from_user.photo else 'No photo available'}</code>\n"  # User profile photo
                    )
                )
                print(
                    f"Sent unauthorized command details to owner: {Config.OWNER_ID} "
                    f"for the message/command '{message.text}' from user '{message.from_user.first_name} {message.from_user.last_name if message.from_user.last_name else ''}' "
                    f"(User  ID: {user_id}) at {timestamp}"
                )
            except Exception as e:
                print(f"Failed to send message to owner: {e}")
            return

    
    # Additional logic for authorized groups can go here

    # Handle authorized users' messages here
    # Check if the message is a command
    if message.text.startswith("/"):
        # If the command is /jl, handle it
        if message.text.startswith("/jl"):
            await main_func(client, message)  # Call the main_func to handle the /jl command
            return

    # If the user sends any other message, you can choose to ignore it or respond accordingly
    # await message.reply("Welcome to the group! How can I assist you?")

@mbot.on_chat_member_updated()
async def handle_chat_member_update(client, chat_member_update):
    # Check if the bot was added to a group
    if chat_member_update.new_chat_member.status == "member" and chat_member_update.new_chat_member.user.is_bot:
        # Send a message to the owner that the bot has been added to a new group
        await mbot.send_message(
            chat_id=Config.OWNER_ID,
            text=f"The bot has been added to a new group: {chat_member_update.chat.title} (ID: {chat_member_update.chat.id})"
        )

# Handle incoming stream recording requests
@mbot.on_message((filters.private | filters.group) & filters.command("jl"))
async def main_func(bot: Client, message) -> None:
    user_id = message.from_user.id  # Get the user ID of the sender

    # Handle authorized users' messages here
    # await message.reply("Welcome to the group! How can I assist you?")
    url_msg = message.text.split(" ")
    if len(url_msg) < 5:  # Expecting 5 parts: command, link, duration, channel, title
        return await message.reply_text(text="""**To record a live link send your link in below format:**

<code>/jl link duration channel title</code>

**Example:**
<code>/jl https://example.com/live-link.m3u8 00:05:00 my_channel my_title</code>

**Note:**<i> Don't report to @SupremeYoriichi and Mr. X if video duration time wrong</i>""")
    else:
        msg_ = await message.reply_text("Please wait ....")
        url = url_msg[1]
        timess = str(url_msg[2])
        channel = url_msg[3]  # New channel parameter
        title = url_msg[4]    # New title parameter
        await uploader_main(url, msg_, timess, message, channel, title)

# Function to run shell commands
async def runcmd(cmd: str) -> Tuple[str, str]:
    """Run command in terminal"""
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    return stdout, stderr

# Function for video recording
async def record_video(usr_link, duration_seconds, video_file_path):
    video_cmd = f'ffmpeg -i "{usr_link}" -c:v copy -map 0:v:0 -map 0:a -f matroska -t {duration_seconds} "{video_file_path}"'
    _LOG.info(f"Running video recording: {video_cmd}")
    stdout_, stderr_ = await runcmd(video_cmd)
    _LOG.info(stdout_)
    _LOG.error(stderr_)

# Function for audio recording
async def record_audio(usr_link, duration_seconds, audio_file_path):
    audio_cmd = f'ffmpeg -y -i "{usr_link}" -map 0:a -c:a copy -t {duration_seconds} "{audio_file_path}"'
    _LOG.info(f"Running audio recording: {audio_cmd}")
    stdout_, stderr_ = await runcmd(audio_cmd)
    _LOG.info(stdout_)
    _LOG.error(stderr_)
    
def TimeFormatter(start_time: str, duration: str) -> str:
    """
    Calculate the end time based on the start time and duration.
    
    :param start_time: Start time in 'HH:MM:SS' format (24-hour format).
    :param duration: Duration in 'HH:MM:SS' format.
    :return: End time in 'HH:MM:SS' format.
    """
    # Parse the start time
    start_time_obj = datetime.strptime(start_time, "%H:%M:%S")
    
    # Parse the duration
    duration_parts = list(map(int, duration.split(':')))
    duration_timedelta = timedelta(hours=duration_parts[0], minutes=duration_parts[1], seconds=duration_parts[2])
    
    # Calculate the end time
    end_time_obj = start_time_obj + duration_timedelta
    
    # Return the end time in 'HH:MM:SS' format
    return end_time_obj.strftime("%H:%M:%S")

async def delete_files(video_file_path: str, audio_file_path: str, thumbnail_file_path: str) -> None:
    try:
        # Delete individual files
        if os.path.exists(video_file_path):
            os.remove(video_file_path)
            _LOG.info(f"Deleted video file: {video_file_path}")
        
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            _LOG.info(f"Deleted audio file: {audio_file_path}")
        
        if os.path.exists(thumbnail_file_path):
            os.remove(thumbnail_file_path)
            _LOG.info(f"Deleted thumbnail file: {thumbnail_file_path}")

        # Get the directory path from the video file path
        video_dir_path = os.path.dirname(video_file_path)

        # Check if the directory is empty before deleting
        if os.path.isdir(video_dir_path) and not os.listdir(video_dir_path):
            os.rmdir(video_dir_path)
            _LOG.info(f"Deleted directory: {video_dir_path}")

    except Exception as e:
        _LOG.error(f"Error deleting files: {e}")

def convert_to_seconds(duration_str: str) -> int:
    """Convert hh:mm:ss format to total seconds."""
    try:
        hours, minutes, seconds = map(int, duration_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        return 0  # Return 0 if the format is incorrect



# Main function to handle the whole process
async def uploader_main(usr_link: str, msg: Message, cb_data: str, message, channel: str, title: str):
    
    # Assuming cb_data is in the format hh:mm:ss
    duration_seconds = convert_to_seconds(cb_data)

    # Get the current time as the start time
    start_time = datetime.now().strftime("%H:%M:%S")
    
    # Calculate the end time using the TimeFormatter function
    end_time = TimeFormatter(start_time, cb_data)

    # Now you can use duration_seconds in your message
    rb_message = await msg.edit(
        text=f"**<code>Starting the recording, please wait now until your time finishes!</code>**\n"
             f"**{cb_data} Recording started for channel:** `{channel}` \n"
             f"**Title:** `{title}`,\n"
             f"<i>This will take {duration_seconds} seconds ...</i>",
        reply_markup=None
    )

    video_dir_path = join(os.getcwd(), Config.DOWNLOAD_DIRECTORY, str(time.time()))
    if not os.path.isdir(video_dir_path):
        os.makedirs(video_dir_path)

    # Use timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    video_file_path = join(video_dir_path, f"{title}_{timestamp}.mkv")
    audio_file_path = join(video_dir_path, f"{title}_{timestamp}.aac")
    thumbnail_file_path = join(video_dir_path, f"{title}_{timestamp}.jpg")  # Path for the thumbnail

    _LOG.info(f"Recording for {duration_seconds} seconds.")

    # Execute both video and audio recordings concurrently
    await asyncio.gather(
        record_video(usr_link, duration_seconds, video_file_path),
        record_audio(usr_link, duration_seconds, audio_file_path)
    )

    # Get Video Duration 
    duration = await get_video_duration(video_file_path)

    # Calculate the timestamp for the thumbnail (middle of the video)
    timestamp = duration / 2 if duration > 0 else 0

    # Generate thumbnail from the recorded video
    await get_thumbnail(video_file_path, thumbnail_file_path, timestamp)

    # Define of_name using title
    of_name = f"{title} - {timestamp}"  # or any other format you prefer
    
    # After recording is done, add metadata to the video
    await add_metadata_to_video(video_file_path, video_file_path, metadata_text, of_name)
    
    # Check if both files exist
    if exists(video_file_path) and exists(audio_file_path):
        # Get current date for filename
        date = datetime.now().strftime("%H-%M-%Y")
        
        # Inside the uploader_main function, after recording is done
        quality, extension = await get_video_info(video_file_path)

        # Create the caption with audio and video details
        cap = f"<b>Filename:</b> <code>{title}.{channel}.{start_time}-{end_time}.{date}.IPTV.WEB-DL.{extension}</code>\n<b>Credits: {Config.CRED_TEXT}<code>{Config.CRED_TEXT}</code>"

        # Check if the video file exists before uploading 
        if not os.path.exists(video_file_path):
            await msg.edit("Video file does not exist.")
            return

        try:
            # Send the video with the caption
            video_message = await mbot.send_video(
                chat_id=message.chat.id,
                video=video_file_path,
                caption=cap,
                thumb=thumbnail_file_path,
                duration=int(duration)
            )
            print(f"[+] Successfully uploaded: {video_file_path}")
            
            # After sending the video, delete the files
            await delete_files(video_file_path, audio_file_path, thumbnail_file_path)
        except Exception as e:
            await msg.edit("Recording failed. Please check the logs for more details.")
            _LOG.error(f"Error during upload: {e}")
    else:
        await msg.edit("Recording failed. Please check the logs for more details.")

metadata_text = "SharkToonsIndia"  # Replace with actual metadata text

async def add_metadata_to_video(input_file: str, output_file: str, metadata_text: str, of_name: str):
    cmd = [
        'ffmpeg', '-y', '-err_detect', 'ignore_err', '-i', input_file, '-c', 'copy',
        '-map', '0', '-c:s', 'copy', '-c:a', 'copy', '-c:v', 'copy',
        '-metadata:s:s', f'title={SharkToonsIndia}',
        '-metadata:s:a', f'title={SharkToonsIndia}',
        '-metadata:s:v', f'title={SharkToonsIndia}',
        '-metadata', f'title={SharkToonsIndia}',
        output_file
    ]

    # Run the command
    stdout, stderr = await runcmd(" ".join(cmd))
    _LOG.info(stdout)
    _LOG.error(stderr)


async def get_video_duration(video_file_path):
    """Get the duration of the video file using ffprobe."""
    try:
        # Use ffprobe to get the duration
        result = await asyncio.to_thread(subprocess.run, 
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())
        return duration  # Return duration in seconds
    except subprocess.CalledProcessError as e:
        print(f"[!] Error getting video duration: {e}")
        return 0  # Return 0 if there's an error

def format_duration(seconds: int) -> str:
    """Format duration from seconds to a string in the format '01hr, 03min, 04sec'."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours}hr, {minutes}min, {seconds}sec"  # Removed leading zeros

def get_file_size(file_path: str) -> str:
    """Get the file size in a human-readable format."""
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        if size_bytes >= 1 << 30:  # GB
            return f"{size_bytes / (1 << 30):.2f} GB"
        elif size_bytes >= 1 << 20:  # MB
            return f"{size_bytes / (1 << 20):.2f} MB"
        elif size_bytes >= 1 << 10:  # KB
            return f"{size_bytes / (1 << 10):.2f} KB"
        else:  # Bytes
            return f"{size_bytes} Bytes"
    return "0 Bytes"

async def get_thumbnail(video_file_path: str, thumbnail_path: str, timestamp: float):
    """Extract a thumbnail from the video at a specific timestamp."""
    try:
        video_file_path = os.path.abspath(video_file_path)
        thumbnail_path = os.path.abspath(thumbnail_path)
        
        result = await asyncio.to_thread(subprocess.run,
            ['ffmpeg', '-y', '-i', video_file_path, '-ss', str(timestamp), '-vframes', '1', thumbnail_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            print(f"Thumbnail extracted successfully: {thumbnail_path}")
        else:
            print(f"[!] Error extracting thumbnail: {result.stderr}")
    except Exception as e:
        print(f"[!] Exception during thumbnail extraction: {e}")

# Progress bar during video upload
async def progress_for_pyrogram(current, total, message, start, file_path):
    now = time.time()
    elapsed_time = now - start
    uploaded_size = current

    # Calculate percentage
    percent = (uploaded_size / total) * 100

    # Calculate blocks for progress bar
    blocks = int(percent // 5)  # Each block represents 5%
    progress_bar = '⬢' * blocks + '⬡' * (20 - blocks)  # 20 blocks total

    # Print simple console output
    print(f"Upload Progress: {percent:.2f}% | Uploaded: {uploaded_size}/{total} bytes")

    # Create a detailed message for the chat
    chat_message = (
        f"<code>[ + ] ......</code> <b>Uploading The File :-</b>\n"
        f"<b>File - Name :-</b> <code>{os.path.basename(file_path)}</code>\n"   
        f"<b>[{progress_bar}]</b>\n"  # Progress bar
        f"<b>Percentage :-</b> <code>{percent:.2f}%</code>\n"  # Percentage display
    )

    # Update the message in the chat
    await rb_message.edit(chat_message)

# Start the bot
if __name__ == "__main__":
    mbot.run()
