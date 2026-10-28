"""
五種對話記憶策略（對應簡報 p31～p33；來源：ai-practice/20_memory_strategies.py）：同一段劇本，換不同記憶策略，比較「記不記得」與「花多少 token」

執行：python p31_memory_strategies.py full        # ① 全量保留
      python p31_memory_strategies.py window      # ② 滑動視窗
      python p31_memory_strategies.py summary     # ③ 摘要壓縮
      python p31_memory_strategies.py vector      # ④ 向量檢索
      python p31_memory_strategies.py structured  # ⑤ 結構化記憶
      python p31_memory_strategies.py all         # 五種依序跑完，最後印對照表

共同介面：每種策略都只做兩件事
  build(user_text)        → 這一輪要送出的 messages（「選」什麼進 context）
  remember(user, reply)   → 呼叫成功後，怎麼「存」這一輪

觀察重點：
  - 劇本第 1 輪交代姓名／過敏／訂單編號，最後一輪考記憶
  - ② 視窗只留 2 輪 → 第 1 輪掉出去就忘了
  - ③ 摘要可能把訂單編號寫錯或漏掉（摘要失真）
  - ④ 能否答對取決於「檢索有沒有命中」
  - ⑤ 關鍵事實存成欄位，每輪都帶，最穩；但多一次抽取呼叫
"""
import json
import math
import re
import sys

from common import client, MODEL_NAME, section

EMBED_MODEL = "bge-m3"   # 平台上的 embedding 模型（④ 向量檢索才會用到）
SYSTEM = {"role": "system", "content": "你是繁體中文旅遊客服助理，每次回答 60 字以內。"}

SCRIPT = [
    "我叫小美，對花生嚴重過敏，訂單編號 A-10234。",
    "下個月想去大阪玩三天，第一天想逛街，去哪一區？",
    "第二天去環球影城要注意什麼？",
    "推薦三樣大阪美食。",
    "我叫什麼名字？訂單編號是多少？飲食上要注意什麼？",   # ← 考記憶
]


def call_llm(messages, max_tokens=200):
    r = client.chat.completions.create(model=MODEL_NAME, messages=messages,
                                       max_tokens=max_tokens, temperature=0.2)
    return r.choices[0].message.content.strip(), r.usage


# ① 全量保留 ─────────────────────────────────────────────
class FullHistory:
    """每次送出完整歷史：最簡單、脈絡最完整，但 prompt_tokens 每輪線性長大"""
    name = "① 全量保留"

    def __init__(self):
        self.history = []

    def build(self, user_text):
        return [SYSTEM] + self.history + [{"role": "user", "content": user_text}]

    def remember(self, user_text, reply):
        self.history += [{"role": "user", "content": user_text},
                         {"role": "assistant", "content": reply}]


# ② 滑動視窗 ─────────────────────────────────────────────
class SlidingWindow(FullHistory):
    """system 永遠保留，其餘只取最近 N 輪；超出視窗的資訊直接消失"""
    name = "② 滑動視窗"
    MAX_TURNS = 2

    def build(self, user_text):
        window = self.history[-self.MAX_TURNS * 2:]          # 1 輪 = user + assistant 2 則
        return [SYSTEM] + window + [{"role": "user", "content": user_text}]


# ③ 摘要壓縮 ─────────────────────────────────────────────
class SummaryMemory(FullHistory):
    """最近 KEEP 輪留原文；更早的對話用「舊摘要 + 新掉出的對話」滾動更新成一段摘要"""
    name = "③ 摘要壓縮"
    KEEP = 2
    PROMPT = ("將以下內容合併成 100 字內的重點紀錄。"
              "保留使用者身分、已確認事實（編號、金額要原樣照抄）與待辦事項，不要加入新資訊。")

    def __init__(self):
        super().__init__()
        self.summary = ""

    def build(self, user_text):
        system = dict(SYSTEM)
        if self.summary:
            system["content"] += f"\n【先前對話摘要】{self.summary}"
        return [system] + self.history + [{"role": "user", "content": user_text}]

    def remember(self, user_text, reply):
        super().remember(user_text, reply)
        old, self.history = self.history[:-self.KEEP * 2], self.history[-self.KEEP * 2:]
        if old:                                               # 有對話掉出視窗才壓縮
            text = "\n".join(f"{m['role']}：{m['content']}" for m in old)
            self.summary, _ = call_llm([
                {"role": "system", "content": self.PROMPT},
                {"role": "user", "content": f"舊摘要：{self.summary or '無'}\n新對話：\n{text}"},
            ])


# ④ 向量檢索 ─────────────────────────────────────────────
def embed(texts):
    r = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in r.data]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


class VectorMemory(SlidingWindow):
    """每輪對話轉成向量存起來；新提問時找出最相關的舊對話，連同最近 N 輪一起送
    實務上 store 換成向量資料庫（Chroma、pgvector、Qdrant…），容量幾乎無上限、可跨對話"""
    name = "④ 向量檢索"
    MAX_TURNS = 2
    TOP_K = 2

    def __init__(self):
        super().__init__()
        self.store = []                                       # [(向量, 使用者提問, 整輪原文)]

    def build(self, user_text):
        messages = super().build(user_text)
        recent = {m["content"] for m in messages}
        q = embed([user_text])[0]
        ranked = sorted(self.store, key=lambda s: cosine(q, s[0]), reverse=True)
        hits = [t for _, u, t in ranked if u not in recent][:self.TOP_K]   # 已在視窗內的不重複帶
        if hits:
            system = dict(SYSTEM)
            system["content"] += "\n【相關的過往對話】\n" + "\n---\n".join(hits)
            messages[0] = system
        self.last_hits = hits
        return messages

    def remember(self, user_text, reply):
        super().remember(user_text, reply)
        text = f"使用者：{user_text}\n助理：{reply}"
        self.store.append((embed([text])[0], user_text, text))


# ⑤ 結構化記憶 ───────────────────────────────────────────
class StructuredMemory(SlidingWindow):
    """從對話抽出關鍵事實存成欄位（JSON），每輪固定放進 system prompt
    和 ④ 的差別：④ 存原文、用到才找；⑤ 存結論、每次都帶"""
    name = "⑤ 結構化記憶"
    MAX_TURNS = 2
    EXTRACT = ("從使用者這句話抽出值得長期記住的事實，只輸出 JSON 物件，沒有就輸出 {}。"
               "可用欄位：name, allergies, order_id, destination, preferences。")

    def __init__(self):
        super().__init__()
        self.profile = {}                                     # 實務上存資料庫，可跨對話

    def build(self, user_text):
        messages = super().build(user_text)
        if self.profile:
            system = dict(SYSTEM)
            system["content"] += "\n【使用者資料】" + json.dumps(self.profile, ensure_ascii=False)
            messages[0] = system
        return messages

    def remember(self, user_text, reply):
        super().remember(user_text, reply)
        raw, _ = call_llm([{"role": "system", "content": self.EXTRACT},
                           {"role": "user", "content": user_text}])
        m = re.search(r"\{.*\}", raw, re.S)                   # 模型常包 ```json，只取大括號
        try:
            facts = json.loads(m.group()) if m else {}
        except json.JSONDecodeError:
            facts = {}
        self.profile.update({k: v for k, v in facts.items() if v})   # 新值覆蓋舊值


# ── 執行 ──────────────────────────────────────────────────
STRATEGIES = {"full": FullHistory, "window": SlidingWindow, "summary": SummaryMemory,
              "vector": VectorMemory, "structured": StructuredMemory}


def run(strategy_cls):
    s = strategy_cls()
    section(s.name)
    total = 0
    for i, text in enumerate(SCRIPT, 1):
        messages = s.build(text)
        reply, usage = call_llm(messages)
        s.remember(text, reply)                               # 呼叫成功之後才存
        total += usage.prompt_tokens
        print(f"\n第 {i} 輪 user：{text}\n   assistant：{reply}")
        print(f"   [送出 {len(messages)} 則｜prompt_tokens = {usage.prompt_tokens:,}]")
    if isinstance(s, SummaryMemory):
        print(f"   [目前摘要] {s.summary}")
    if isinstance(s, VectorMemory):
        print(f"   [最後一輪檢索命中] {[h.split(chr(10))[0] for h in s.last_hits]}")
    if isinstance(s, StructuredMemory):
        print(f"   [使用者資料] {json.dumps(s.profile, ensure_ascii=False)}")
    return s.name, total, reply


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    keys = list(STRATEGIES) if which == "all" else [which]
    results = [run(STRATEGIES[k]) for k in keys]
    if len(results) > 1:
        section("對照表（不含摘要／抽取／embedding 的額外呼叫）")
        for name, total, last in results:
            print(f"{name:<8} 對話 prompt_tokens 合計 {total:>6,}｜最後一輪回答：{last[:50]}")
