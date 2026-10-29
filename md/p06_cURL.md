### 先設定 API Key

```powershell
$env:MODA_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxx"
```
### 用指令送出網路請求 cURL
```
curl.exe --location "https://modaone-llm-api.dginfra.gov.tw/api/v1/chat/completions" `
    --header "Content-Type: application/json" `
    --header "X-API-KEY: $env:MODA_API_KEY" `
    --data '{\"model\": \"gemma-4-31B-it\", \"messages\": [{\"role\": \"user\", \"content\": \"你好\"}]}'
```
### 設定編碼
```
[Console]::OutputEncoding = [Text.Encoding]::UTF8
```
```
$resp = curl.exe -s --location "https://modaone-llm-api.dginfra.gov.tw/api/v1/chat/completions" `
    --header "Content-Type: application/json" `
    --header "X-API-KEY: $env:MODA_API_KEY" `
    --data '{\"model\": \"gemma-4-31B-it\", \"messages\": [{\"role\": \"user\", \"content\": \"你好\"}]}' |
    ConvertFrom-Json
```

### 展開完整 JSON
```
$resp | ConvertTo-Json -Depth 10      # 展開完整 JSON
```
### 只看回答
```
$resp.choices[0].message.content    
```


### Invoke-RestMethod 是 PowerShell 內建、專門用來呼叫 REST API 的指令
```
Invoke-RestMethod -Method Post `
    -Uri "https://modaone-llm-api.dginfra.gov.tw/api/v1/chat/completions" `
    -Headers @{ "X-API-KEY" = $env:MODA_API_KEY } `
    -ContentType "application/json; charset=utf-8" `
    -Body ([Text.Encoding]::UTF8.GetBytes('{"model": "gemma-4-31B-it", "messages": [{"role": "user", "content": "你好"}]}'))
```

```
$raw = Invoke-WebRequest -Method Post -UseBasicParsing `
    -Uri "https://modaone-llm-api.dginfra.gov.tw/api/v1/chat/completions" `
    -Headers @{ "X-API-KEY" = $env:MODA_API_KEY } `
    -ContentType "application/json; charset=utf-8" `
    -Body ([Text.Encoding]::UTF8.GetBytes('{"model": "gemma-4-31B-it", "messages": [{"role": "user", "content": "你好"}]}'))

```
### 處理中文亂碼的問題
```
$resp = [Text.Encoding]::UTF8.GetString($raw.RawContentStream.ToArray()) | ConvertFrom-Json
```


### 加上系統提示詞，明確告訴它要用繁體中文
```
$raw = Invoke-WebRequest -Method Post -UseBasicParsing `
    -Uri "https://modaone-llm-api.dginfra.gov.tw/api/v1/chat/completions" `
    -Headers @{ "X-API-KEY" = $env:MODA_API_KEY } `
    -ContentType "application/json; charset=utf-8" `
    -Body ([Text.Encoding]::UTF8.GetBytes('{"model": "gemma-4-31B-it", "messages": [{"role": "system", "content": "你是台灣的助理，請一律使用繁體中文（臺灣用語）回答。"}, {"role": "user", "content": "你好"}]}'))

```