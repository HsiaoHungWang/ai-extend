"""
記憶策略實作②：摘要壓縮（對應簡報 p33 summary_memory.py）
執行：python p33_summary_memory.py

  最近 keep 則訊息保留原文；更早的對話請模型濃縮成一段摘要，換掉原本那一大串
  觀察重點：
    - 每次壓縮印出摘要：名字、過敏、訂單編號 A-10234 有沒有被正確保留？（摘要失真）
    - 第 7 輪考記憶：第 1 輪早已不在原文裡，只能靠摘要回答
"""
from common import client, MODEL_NAME, section

SYSTEM = {"role": "system", "content": "你是繁體中文旅遊客服助理，每次回答 60 字以內。"}
summary_tokens = 0       # 摘要呼叫累計花掉的 token（對照投影片「成本效益」）


def call_llm(messages, max_tokens=300):
    r = client.chat.completions.create(model=MODEL_NAME, messages=messages,
                                       max_tokens=max_tokens, temperature=0.2)
    call_llm.usage = r.usage                     # 留著最後一次的 usage，給呼叫端查看
    return r.choices[0].message.content.strip()


# ===== 以下對應投影片 =====
SUMMARY_PROMPT = ("請將以下對話濃縮成 200 字內的重點紀錄，"
                  "保留使用者身分、已確認事實與待辦事項，不要加入新資訊。")


def compress(history, keep=4):
    old, recent = history[:-keep], history[-keep:]
    if len(old) < 4:
        return history

    text = "\n".join(f"{m['role']}: {m['content']}" for m in old)
    summary = call_llm([{"role": "system", "content": SUMMARY_PROMPT},
                        {"role": "user",   "content": text}])

    return [{"role": "system",
             "content": f"【先前對話摘要】{summary}"}] + recent
# ===== 投影片範圍結束 =====


def chat(history, user_text):
    history.append({"role": "user", "content": user_text})

    # 摘要合併進 system：部分模型不接受兩則 system 訊息
    if history[0]["role"] == "system":
        system = {"role": "system", "content": SYSTEM["content"] + "\n" + history[0]["content"]}
        messages = [system] + history[1:]
    else:
        messages = [SYSTEM] + history

    reply = call_llm(messages, max_tokens=200)
    history.append({"role": "assistant", "content": reply})
    print(f"   [送出 {len(messages)} 則｜prompt_tokens = {call_llm.usage.prompt_tokens:,}]")
    return reply


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
    section("摘要壓縮：keep = 4（最近 2 輪留原文）")
    history = []
    for i, text in enumerate(SCRIPT, 1):
        print(f"\n第 {i} 輪 你：{text}")
        print(f"   助理：{chat(history, text)}")

        before = len(history)
        history = compress(history)              # 每輪結束後檢查要不要壓
        if len(history) < before:
            summary_tokens += call_llm.usage.total_tokens
            print(f"   🗜️ 壓縮：{before} 則 → {len(history)} 則｜這次摘要花 {call_llm.usage.total_tokens:,} tokens")
            print(f"   【摘要】{history[0]['content']}")

    print(f"\n👉 摘要呼叫累計花了 {summary_tokens:,} tokens，換來每輪 prompt_tokens 不再一路變大")
    print("👉 檢查摘要裡的訂單編號是不是 A-10234：重要事實建議另外存成結構化欄位（見 p31_memory_strategies.py structured）")
