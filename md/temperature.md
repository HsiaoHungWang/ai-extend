## temperature 控制隨機性，越高越發散
0–2（OpenAI 規格）；AFS 文件只寫「大於 0」預設1.0，使用建議：客服／擷取 0.1–0.3、文案 0.7–1.0、一般很少超過 1

### 設定四個溫度，每個溫度跑10次，觀察回傳的結果
```
from collections import Counter

for t in [0.0, 0.5, 1.0, 1.5]:
    names = []
    for i in range(10):
        r = client.chat.completions.create(
            model=MODEL_NAME, temperature=t, top_p=1, max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )
        names.append(r.choices[0].message.content.strip())
    c = Counter(names)
    print(f"temperature={t}：{len(c)} 種 → {dict(c)}")

```
### 設定四個溫度，每個溫度跑10次，每一次執行都要改變 seed 的值，觀察回傳的結果
```
from collections import Counter

for t in [0.0, 0.5, 1.0, 1.5]:
    names = []
    for i in range(10):
        r = client.chat.completions.create(
            model=MODEL_NAME, temperature=t, top_p=1, max_tokens=50,seed=i,
            messages=[{"role": "user", "content": prompt}],
        )
        names.append(r.choices[0].message.content.strip())
    c = Counter(names)
    print(f"temperature={t}：{len(c)} 種 → {dict(c)}")

```
ModaOne 的 seed 預設是 42，同樣的請求會得到同樣的答案