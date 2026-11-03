"""
Token 是什麼？先估再送，最後對照 usage
執行：python p28_token_count.py
套件：pip install tiktoken

  一、用 tiktoken 估算：中文、英文、JSON、空白換行各算幾個 token
  二、沒有 tiktoken 時的粗估法：中文字數 × 1 + 英文單字數 × 1.3
  三、真的呼叫一次 API，拿估算值對照回應中的 usage（計費以 usage 為準）
"""
import json
import re
import unicodedata

from common import client, MODEL_NAME, section

try:
    import tiktoken
    enc = tiktoken.get_encoding("o200k_base")          # OpenAI GPT-4o 系列的斷詞器
except Exception as e:                                 # 沒裝套件，或第一次下載編碼表失敗
    print(f"⚠️ tiktoken 無法使用（{type(e).__name__}），以下只顯示粗估值")
    enc = None


def count_tokens(text: str):
    """tiktoken 估算值；沒有 tiktoken 時回傳 None"""
    return len(enc.encode(text)) if enc else None


def rough_estimate(text: str) -> int:
    """粗估法：中文字數 × 1 + 英文單字數 × 1.3"""
    chinese = len(re.findall(r"[一-鿿]", text))
    english = len(re.findall(r"[A-Za-z]+", text))
    return round(chinese * 1 + english * 1.3)


def pad(text: str, width: int) -> str:
    """中文字在終端機佔兩格，補空白讓表格對齊"""
    w = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)
    return text + " " * max(width - w, 0)


# ---------- 一、二：同樣的意思，換個寫法，token 數差很多 ----------
section("一、估算 token 數")

data = {"order_id": "A1234", "status": "退貨處理中", "days": 7}
samples = {
    "中文問句":       "請問退貨流程要多久？",
    "英文問句":       "How long does the return process take?",
    "JSON（縮排）":   json.dumps(data, ensure_ascii=False, indent=4),
    "JSON（壓縮）":   json.dumps(data, ensure_ascii=False, separators=(",", ":")),
    "同一句加空白換行": "請問    退貨流程\n\n\n要多久？    ",
}

print(f"{pad('內容', 18)}{pad('字元數', 8)}{pad('tiktoken', 10)}粗估")
for name, text in samples.items():
    tk = count_tokens(text)
    print(f"{pad(name, 18)}{pad(str(len(text)), 8)}{pad(str(tk) if tk is not None else '-', 10)}{rough_estimate(text)}")

print("\n👉 JSON 的引號、括號、縮排都要算；空白與換行也算 token")


# ---------- 三：送出前先估，送出後對照 usage ----------
section("二、呼叫 API，對照 usage")

messages = [
    {"role": "system", "content": "你是電商客服，用繁體中文回答，50 字以內。"},
    {"role": "user",   "content": "請問退貨流程要多久？"},
]
content_text = "".join(m["content"] for m in messages)
print("送出前估算（只算文字內容）")
print("  tiktoken:", count_tokens(content_text) if enc else "-")
print("  粗估法  :", rough_estimate(content_text))

response = client.chat.completions.create(
    model = MODEL_NAME,
    temperature = 0.3,
    max_tokens = 200,
    messages = messages,
)

print("\n模型回覆：", response.choices[0].message.content.strip())

u = response.usage
print("\n--- usage（實際計費以這裡為準）---")
print("  prompt_tokens     （輸入）:", u.prompt_tokens)
print("  completion_tokens （輸出）:", u.completion_tokens)
print("  total_tokens      （合計）:", u.total_tokens)

reply = response.choices[0].message.content
if enc:
    print(f"\n用 tiktoken 估同一段回覆：{count_tokens(reply)}  vs  usage.completion_tokens：{u.completion_tokens}")

print("\n👉 為什麼估算和 usage 對不上？")
print("   1. 斷詞器不同：tiktoken 是 OpenAI 的，ModaOne 上的模型用自己的斷詞器")
print(f"   2. 包裝成本：role 標記、對話模板等格式也算進 prompt_tokens（目前模型：{MODEL_NAME}）")
