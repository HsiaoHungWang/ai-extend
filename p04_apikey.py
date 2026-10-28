from getpass import getpass
from dotenv import load_dotenv
import os

# load_dotenv()  # Load environment variables from .env file  
# load_dotenv(override=True)  #.env 優先，會覆蓋系統環境變數
API_KEY = os.environ.get("KEY1") #or getpass("Enter your API key: ")

print(f"Your API key1 is: {API_KEY[:6]}...{API_KEY[-4:]}" if API_KEY else "找不到 KEY1")
