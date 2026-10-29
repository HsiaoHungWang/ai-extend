"""
比較 stream=False 與 stream=True 的差別
執行：python p21_stream.py          # 國網中心端點
      python p21_stream.py moda     # ModaOne 端點

看什麼：
  - stream=False：等很久 → 整篇一次出現（第一個字時間 ≈ 總時間）
  - stream=True ：很快開始 → 一個字一個字冒出來（第一個字時間 ≪ 總時間）
"""
import random
import sys
import time

from openai import OpenAI
from common import API_KEY

HOSTS = {
    "nchc": "https://portal.genai.nchc.org.tw/api/v1",
    "moda": "https://modaone-llm-api.dginfra.gov.tw/api/v1",
}
client = OpenAI(api_key=API_KEY, base_url=HOSTS[sys.argv[1] if len(sys.argv) > 1 else "nchc"])

MODEL  = "Mistral-Large-3-675B-Instruct-2512"
PROMPT = "請寫一篇以未來城市為背景的短篇小說："


def ask(stream):
    print(f"\n===== stream={stream} =====")
    start, first = time.time(), None
    r = client.completions.create(model=MODEL, prompt=PROMPT, max_tokens=500, stream=stream)

    if stream:
        for chunk in r:                       # 收到一塊印一塊
            if chunk.choices and chunk.choices[0].text:
                first = first or time.time() - start
                print(chunk.choices[0].text, end="", flush=True)
    else:
        first = time.time() - start           # 整篇一次回來
        print(r.choices[0].text)
    total = time.time() - start
    print(f"\n⏱ 第一個字：{first or total:.2f} 秒｜總時間：{total:.2f} 秒")


ask(stream=False)
ask(stream=True)