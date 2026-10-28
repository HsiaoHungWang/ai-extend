# ai-extend：Notebook 以外的延伸範例

上課範例以 `../Moda_API_v3-2-3.ipynb` 為主；notebook 沒有提供的程式範例，從 `../ai-practice` 挑選搬到這裡。
結構與 `ai-practice` 相同：每支範例都從 `common.py` 取得 client 與參數。

## 環境準備（Windows PowerShell）

```powershell
cd ai-extend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # 填入 API_KEY；或直接複製 ..\ai-practice\.env
python -c "from common import client; print([m.id for m in client.models.list().data])"   # 確認金鑰可用
```

## 資料夾結構

```
ai-extend/
├─ .env.example        金鑰範本（複製成 .env 後填入，.env 不上傳 Git）
├─ .gitignore          忽略 .env、.venv/、__pycache__/、logs/
├─ .vscode/settings.json
├─ common.py           共用設定：金鑰、端點、模型名稱、client、section()
├─ requirements.txt    搬入範例時依需要補套件
├─ logs/               執行紀錄（jsonl、csv）
└─ README.md
```

## 檔案對照

搬入範例後，在下表補一列（檔名可重新編號，建議保留「對應簡報頁」方便上課查找）：

| 檔案 | 用途 | 對應簡報頁 | 執行方式 |
|---|---|---|---|
| `common.py` | 環境準備（金鑰、端點、client） | — | 由其他檔案匯入，不直接執行 |
| `p28_token_count.py` | tiktoken 估算 token，對照回應的 usage | p28 | `python p28_token_count.py` |
| `p32_sliding_window.py` | 滑動視窗（函式版，程式碼同投影片）：system 永遠保留＋最近 5 輪；第 7 輪考記憶 | p32 | `python p32_sliding_window.py` |
| `p33_summary_memory.py` | 摘要壓縮（函式版，程式碼同投影片）：舊對話濃縮成摘要，觀察摘要失真與成本 | p33 | `python p33_summary_memory.py` |
| `p31_memory_strategies.py` | 【課後延伸】五種記憶策略對照（class 版）：① 全量 ② 滑動視窗 ③ 摘要壓縮 ④ 向量檢索（bge-m3）⑤ 結構化記憶；同一劇本比較記憶與 token | p31～p33 | `python p31_memory_strategies.py <full\|window\|summary\|vector\|structured\|all>` |
| `p35_prompt_assembly.py` | 提示詞組裝：固定模板 + 動態資料 + 用 ### 分隔使用者輸入 | p35 | `python p35_prompt_assembly.py` |
| `p35_memory_basics.py` | 最簡單的記憶層：存、選（最近 2 輪）、壓（摘要）、找（長期記憶） | p35 | `python p35_memory_basics.py` |
| `p40_guard_basics.py` | 防護觀測：輸入過濾與遮罩、輸出禁用字檢查、呼叫日誌（logs/）、成本上限 | p40 | `python p40_guard_basics.py` |
| `responses_previous_id.py` | Responses API 多輪對話（OpenAI 官方端點，需 `OPENAI_API_KEY`）：① `previous_response_id` 接續、不存 history，觀察 input_tokens 仍累加 ② 斷鏈即失憶 | — | `python responses_previous_id.py` |

## 從 ai-practice 搬檔時注意

- **相依檔案要一起搬**：
  - `10`～`13` 匯入 `harness.py`；`11`、`13` 還會匯入 `07_tool_call.py`（沿用假資料庫與查詢函式）
  - `12_production.py eval` 需要 `eval_cases.json`
- 模型名稱、端點一律從 `common.py` 匯入（`MODEL_NAME`、`VLM_MODEL`、`TOOL_MODEL`、`API_BASE`），不要寫死在範例裡。
- 有額外套件的範例（例如 LangChain），記得補進 `requirements.txt`。
