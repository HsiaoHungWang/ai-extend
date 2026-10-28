"""
共用設定：所有練習程式都從這裡取得 client 與參數（對應 notebook 第 0 段「環境準備」）

金鑰：讀取同資料夾 .env 的 MODAONE_API_KEY 或 API_KEY；都沒有就用 getpass 現場輸入
模型：可在 .env 設定 MODAONE_MODEL / MODAONE_VLM_MODEL / MODAONE_TOOL_MODEL 覆寫預設值

⚠️ API_BASE 只保留到 /api/v1 為止：
   金鑰管理頁面複製到的通常是完整的 .../api/v1/chat/completions，
   整串當成 base_url 的話，openai 套件會再自己接一次 /chat/completions → 路徑重複變 404
"""
import os
from getpass import getpass

from dotenv import load_dotenv
from openai import OpenAI

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))   # 明確指定路徑：從別的資料夾執行也讀得到

API_BASE   = os.environ.get("MODAONE_API_BASE", "https://modaone-llm-api.dginfra.gov.tw/api/v1")
MODEL_NAME = os.environ.get("MODAONE_MODEL", "gemma-4-31B-it")        # 文字模型
VLM_MODEL  = os.environ.get("MODAONE_VLM_MODEL", "gemma-4-31B-it")    # 看圖模型（需支援圖像）
TOOL_MODEL = os.environ.get("MODAONE_TOOL_MODEL", "gemma-4-31B-it")   # 工具呼叫模型

API_KEY = (os.environ.get("MODAONE_API_KEY") or os.environ.get("API_KEY")
           or getpass("請貼上 API 金鑰：")).strip()

# OpenAI 相容端點：直接用官方 openai 套件
client = OpenAI(api_key=API_KEY, base_url=API_BASE)


def section(title: str):
    """印出分段標題，讓終端機輸出比較好讀"""
    print(f"\n{'=' * 12} {title} {'=' * 12}")
