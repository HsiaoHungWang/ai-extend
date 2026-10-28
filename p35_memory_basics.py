"""
最簡單的記憶層：存、選、壓、找
執行：python p35_memory_basics.py

  存：每輪成功後，把提問與回答寫進 history
  選：送出時只帶最近 KEEP 輪原文
  壓：超出視窗的舊對話，濃縮成一段摘要
  找：長期記憶不放在對話裡，問題相關時才找出來帶上
"""
from common import client, MODEL_NAME

KEEP = 2                 # 選：只帶最近 2 輪原文
history = []             # 存：完整的對話紀錄
summary = ""             # 壓：舊對話的摘要
summarized = 0           # history 中已經被摘要過的位置

# 找：長期記憶（實務上存在資料庫；這裡用「關鍵字 → 事實」示範）
LONG_TERM = [
    (["吃", "餐", "美食", "點心"], "使用者對花生嚴重過敏"),
    (["住", "交通", "機場"],       "使用者住在台北"),
]


def store(question, answer):                       # 存
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})


def select():                                      # 選
    return history[-KEEP * 2:]                     # 取 history 最後 4 個元素，也就是最近 2 輪對話。


def compress():                                    # 壓
    global summary, summarized                     # 宣告全域變數
    old = history[summarized:-KEEP * 2]            # 掉出視窗、還沒摘要過的部分
    if not old:
        return

    # 呼叫一次模型，請它幫忙寫摘要。這裡用「舊摘要 + 新對話」的方式，讓模型知道要保留哪些資訊。
    text = "\n".join(f"{m['role']}：{m['content']}" for m in old)
    resp = client.chat.completions.create(model=MODEL_NAME, max_tokens=200, messages=[
        {"role": "user", "content": f"把以下內容合併成 80 字內的摘要，保留人名、地點、偏好：\n"
                                    f"舊摘要：{summary or '無'}\n新對話：\n{text}"}])
    summary = resp.choices[0].message.content.strip()
    summarized = len(history) - KEEP * 2


def find(question):                                # 找
    return [fact for keywords, fact in LONG_TERM if any(k in question for k in keywords)]


def chat(question):
    system = "你是旅遊助理，用繁體中文回答，60 字以內。"
    if summary:
        system += f"\n先前對話摘要：{summary}"
    facts = find(question)
    if facts:
        system += "\n關於使用者：" + "；".join(facts)

    window = select()
    messages = [{"role": "system", "content": system}] + window + [{"role": "user", "content": question}]
    resp = client.chat.completions.create(model=MODEL_NAME, max_tokens=200, messages=messages)
    answer = resp.choices[0].message.content.strip()

    store(question, answer)       # 呼叫成功之後才存
    compress()                    # 存完再檢查要不要壓

    print(f"\n你：{question}")
    print(f"助理：{answer}")
    print(f"  [選] 帶了最近 {len(window) // 2} 輪原文｜[找] {facts or '無'}｜[壓] 摘要：{summary or '（尚無）'}")


if __name__ == "__main__":
    for q in ["我叫小美，下個月要去大阪玩三天。",
              "第一天想逛街，去哪一區？",
              "第二天去環球影城要注意什麼？",
              "推薦三樣大阪美食。",            # 找：觸發「花生過敏」
              "我叫什麼名字？要去哪裡玩？"]:     # 壓：第 1 輪早已掉出視窗，靠摘要回答
        chat(q)
