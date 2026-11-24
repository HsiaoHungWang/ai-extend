from getpass import getpass
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file  
# load_dotenv(override=True)  #.env 優先，會覆蓋系統環境變數
API_KEY = (os.environ.get("API_KEY") or "").strip()
if not API_KEY.startswith("sk-"):
    API_KEY = getpass("Enter your API key: ").strip()

print(f"Your API_KEY is: {API_KEY[:6]}...{API_KEY[-4:]}" if API_KEY else "找不到 API_KEY")
