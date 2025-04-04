import os

class Config(object):
    # API credentials
    API_ID = int(os.environ.get("API_ID", ))  # Replace with your actual API ID Ex 152002 don't use inverted commas here
    API_HASH = os.environ.get("API_HASH", "")  # Replace with your actual API Hash
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")  # Replace with your actual Bot Token

    # Owner ID
    OWNER_ID = int(os.environ.get("OWNER_ID", 6066102279))  # Replace with your actual Owner ID

    # Download directory
    DOWNLOAD_DIRECTORY = os.environ.get("DOWNLOAD_DIRECTORY", "./downloads")  # Default download directory

    # Optional: Add any other configuration variables you need
    PM_AUTH_USERS = list(int(x) for x in os.environ.get("PM_AUTH_USERS", "6066102279").split())  # Replace with actual user IDs
    CHAT_ID = int(os.environ.get("CHAT_ID", -1002414124327))  # Replace with actual group ID

    # Credential text
    CRED_TEXT = os.environ.get("CRED_TEXT", "SHARKTOONSINDIA")  # Default value for CRED_TEXT, Don't Remove If You Respect The Developer