"""
記憶策略實作①：滑動視窗（對應簡報 p32 sliding_window.py）
執行：python p32_sliding_window.py

  system 永遠保留，其餘只取最近 MAX_TURNS 輪
  觀察重點：
    - prompt_tokens 長到一定程度就不再變大 → 成本可預測
    - 第 7 輪考記憶時，第 1 輪早已滑出視窗 → 名字、訂單編號答不出來
"""
from common import client, MODEL_NAME, section

MODEL = MODEL_NAME

# ===== 以下對應投影片 =====
SYSTEM = {"role": "system", "content": "你是繁體中文旅遊客服助理，每次回答 60 字以內。"}
history = []             # 只存 user / assistant，不含 system
MAX_TURNS = 5            # 保留最近 5 輪（= 10 則訊息）


def chat(user_text):
    history.append({"role": "user", "content": user_text})

    # 關鍵：system 永遠保留，其餘只取最後 N 輪
    messages = [SYSTEM] + history[-MAX_TURNS * 2:]

    r = client.chat.completions.create(
        model=MODEL, messages=messages,
        max_tokens=200)                  # 投影片沒有這個參數：控制示範成本
    reply = r.choices[0].message.content

    history.append({"role": "assistant", "content": reply})
    print(f"   [送出 {len(messages)} 則｜history 共 {len(history)} 則｜"
          f"prompt_tokens = {r.usage.prompt_tokens:,}]")
    return reply
# ===== 投影片範圍結束 =====


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
    section(f"滑動視窗：MAX_TURNS = {MAX_TURNS}")
    for i, text in enumerate(SCRIPT, 1):
        print(f"\n第 {i} 輪 你：{text}")
        print(f"   助理：{chat(text).strip()}")

    print("\n👉 第 1 輪已經滑出視窗：送出的訊息裡沒有名字和訂單編號，模型只能說不知道（或亂猜）")
    print("👉 試試把 MAX_TURNS 改成 10 再跑一次：答得出來了，但 prompt_tokens 也一路變大")
