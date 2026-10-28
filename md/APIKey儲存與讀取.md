# 方法一 Windows PowerShell
## 儲存(臨時)：只在目前視窗有效，關掉就消失
```
$env:KEY1 = "sk-xxxx"
```
## 讀取()
```
$env:KEY1
```
## 儲存(永久)：寫入使用者層級
```
[Environment]::SetEnvironmentVariable("KEY2", "sk-xxxx", "User")

```
## 讀取：視窗要先關掉再開啟才讀得到
```
[Environment]::GetEnvironmentVariable("KEY2", "User")

```
## Python 從環境變數讀取
```
import os
API_KEY = os.environ.get("KEY1")
```

# 方法二 .env 檔
格式規則：一行一個變數、`=` 兩側不要留空白
## 儲存
```
KEY1=sk-xxxx
```

## 讀取
先安裝 python-dotenv 套件
```
pip install python-dotenv
```
```
import os
from dotenv import load_dotenv

load_dotenv()    # 把 .env 的內容載入到 os.environ
# load_dotenv(override=True)  #.env 優先，會覆蓋系統環境變數
api_key = os.environ.get("KEY1") 
```

# 方法三 getpass 執行時輸入
```
from getpass import getpass
API_KEY = getpass("請輸入你的 API 金鑰：")
```