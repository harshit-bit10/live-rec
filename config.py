import os

class Config(object):
    # API credentials
    API_ID = int(os.environ.get("API_ID",17108931 ))  # Replace with your actual API ID Ex 152002 don't use inverted commas here
    API_HASH = os.environ.get("API_HASH", "436b24700208cae55ded351d8f25fd7a")  # Replace with your actual API Hash
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7129828945:AAEXgYw4HhToIcgWrJcoo17R1EvdI0lts2I")  # Replace with your actual Bot Token

    # Owner ID
    OWNER_ID = int(os.environ.get("OWNER_ID", 5300197778))  # Replace with your actual Owner ID

    # Download directory
    DOWNLOAD_DIRECTORY = os.environ.get("DOWNLOAD_DIRECTORY", "./downloads")  # Default download directory

    # Optional: Add any other configuration variables you need
    PM_AUTH_USERS = list(int(x) for x in os.environ.get("PM_AUTH_USERS", "5300197778").split())  # Replace with actual user IDs
    CHAT_ID = int(os.environ.get("CHAT_ID", -1002525317083))  # Replace with actual group ID

    # Credential text
    CRED_TEXT = os.environ.get("CRED_TEXT", "@Kushi_Yarige_bedda")  # Default value for CRED_TEXT, Don't Remove If You Respect The Developer
