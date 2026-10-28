"""
Responses API 多輪對話：用 previous_response_id 接續（OpenAI 官方端點）
執行：python responses_previous_id.py

  對照 p32_sliding_window.py：
    - Chat Completions：自己把 user / assistant 存進 history 陣列，每輪整串重送
    - Responses API  ：每輪只送「這一句」，用 previous_response_id 指向上一輪，伺服器幫你接上
  觀察重點：
    ① 程式裡沒有 history 陣列，第 7 輪仍記得第 1 輪的名字與訂單編號
    ② input_tokens 仍一輪比一輪大 → 不用重送 ≠ 不用付費
    ③ instructions 不會被繼承，每輪都要重新傳
    ④ 斷鏈（不帶 previous_response_id）→ 模型立刻失憶

金鑰：.env 的 OPENAI_API_KEY；模型可用 OPENAI_MODEL 覆寫（預設 gpt-4.1-mini）
"""
import os
from getpass import getpass

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY") or getpass("請貼上 OpenAI API 金鑰："))
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

INSTRUCTIONS = "你是繁體中文旅遊客服助理，每次回答 60 字以內。"
last_id = None           # 唯一要記的狀態：上一輪的 response id（取代 history 陣列）


def chat(user_text, keep_chain=True):
    global last_id
    previous = last_id if keep_chain else None
    r = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,        # 不會繼承 → 每輪都要傳
        input=user_text,                  # 只送這一句
        previous_response_id=previous,    # 指向上一輪，伺服器接上歷史
        max_output_tokens=200,            # 控制示範成本
    )
    print(f"   [previous = {previous or '無'}｜input_tokens = {r.usage.input_tokens:,}]")
    last_id = r.id
    return r.output_text


SCRIPT = [
    "我叫小美，對花生嚴重過敏，訂單編號 A-10234。",
    "下個月想去大阪玩三天，第一天想逛街，去哪一區？",
    "第二天去環球影城要注意什麼？",
    "第三天想去京都，交通怎麼安排？",
    "推薦三樣大阪美食。",
    "有什麼適合買回台灣的伴手禮？",
    "我叫什麼名字？訂單編號是多少？飲食上要注意什麼？",   # ← 考記憶
]

if __name__ == "__main__":
    print(f"模型：{MODEL}")

    print("\n============ ① 用 previous_response_id 串起 7 輪對話 ============")
    for i, text in enumerate(SCRIPT, 1):
        print(f"\n第 {i} 輪 你：{text}")
        print(f"   助理：{chat(text).strip()}")
    print("\n👉 沒有 history 陣列，第 7 輪仍記得：伺服器幫你接上了")
    print("👉 但 input_tokens 一路變大：前面的對話照樣計費")

    print("\n============ ② 斷鏈：不帶 previous_response_id ============")
    print(f"\n你：{SCRIPT[-1]}")
    print(f"   助理：{chat(SCRIPT[-1], keep_chain=False).strip()}")
    print("\n👉 沒指向上一輪 → 模型失憶；長期記憶要自己存，再放進 instructions 注入")
