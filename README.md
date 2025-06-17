# 女優分類系統 v5.1

一個功能完整的女優分類與管理系統，支援互動式分類、片商分類、檔案整理等功能。

## ✨ 主要功能

### 🔍 掃描與搜尋
- 自動掃描影片檔案並建立資料庫
- 智慧提取影片編號
- **智慧過濾功能**：自動跳過 FC2、FC2PPV、PPV 等相關檔案，避免無效搜尋
- **增強版網路搜尋女優資訊（v5.1 新功能）**
  - 同步搜尋並儲存片商資訊（片商名稱、片商代碼）
  - 自動提取發行日期資訊
  - 支援多種片商代碼映射關係
  - 建立完整的影片、女優與片商關聯資料庫
- 建立完整的影片與女優關聯資料庫

### 🤝 互動式分類
- 多女優共演時提供選擇對話框
- 支援個人偏好設定與記憶
- 自動標籤檔名（標記所有參演女優）
- 智慧分類建議

### 📁 標準分類
- 使用第一位女優進行快速分類
- 批次檔案移動
- 自動建立女優資料夾

### 🏢 片商分類（新功能）
- 分析女優的片商分佈統計
- 依信心度自動歸類到片商資料夾
- 可自訂分類規則與門檻
- 支援備份與復原

### ⚙️ 偏好設定
- 最愛女優與優先女優設定
- 共演記錄管理
- 片商分類規則設定
- 檔案命名選項設定

## 安裝說明

### 環境需求
- Python 3.8 或以上版本
- [其他相依套件]

### 安裝步驟
```bash
# 1. 複製專案
git clone [repository-url]
cd 女優分類

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安裝相依套件
pip install -r requirements.txt

# 4. 設定環境變數
cp .env.example .env
# 編輯 .env 檔案填入必要的設定

# 5. 執行資料庫遷移（如適用）
python manage.py migrate

# 6. 啟動服務
python main.py
```

## 使用說明
[填寫如何使用這個專案]

## 開發指南

### 目錄結構
```
女優分類/
├── src/                    # 主要程式碼
├── tests/                  # 測試程式
├── .ai-playground/         # AI 實驗區
├── docs/                   # 專案文件
├── config/                 # 設定檔案
├── scripts/                # 工具腳本
└── 專案管理/               # 業務文件
```

### 開發流程
1. 建立功能分支：`git checkout -b feature/功能名稱`
2. 開發功能並撰寫測試
3. 執行測試：`pytest tests/`
4. 提交變更：遵循 commit message 規範
5. 建立 Pull Request

### AI Agent 使用規範
- 實驗性程式碼放在 `.ai-playground/experiments/`
- 功能驗證檔案放在 `.ai-playground/validations/`
- 完成驗證後移動到 `.ai-playground/archived/`
- 檔案命名使用時間戳記格式

### 測試
```bash
# 執行所有測試
pytest tests/

# 執行特定測試
pytest tests/test_specific.py

# 生成測試覆蓋率報告
pytest --cov=src tests/
```

## API 文件
[如果是 API 專案，提供 API 文件連結或說明]

## 部署說明
[填寫部署相關資訊]

## 貢獻指南
1. Fork 這個專案
2. 建立您的功能分支
3. 提交您的變更
4. 推送到分支
5. 建立 Pull Request

## 版本歷史
- v1.0.0 - 初始版本 (2025-06-17)

## 授權條款
[填寫授權資訊]

## 聯絡資訊
- 專案維護者: [您的名字]
- Email: [您的 Email]
- 專案網址: [專案網址]

## 致謝
感謝所有為這個專案做出貢獻的人員。

## 疑難排解
### 常見問題
Q: [問題描述]
A: [解答]

### 取得協助
如果遇到問題，請：
1. 查看 [FAQ](docs/faq.md)
2. 搜尋現有的 [Issues](issues)
3. 建立新的 Issue 描述問題

## 2025-06-18 優化更新

### FC2/PPV 檔案自動過濾
- 增強 `UnifiedCodeExtractor` 的過濾功能
- 自動跳過 FC2、FC2PPV、PPV 相關檔案，避免無效搜尋
- 支援的過濾模式：
  - `FC2-`, `FC2_`, `FC2PPV-`, `FC2PPV_`
  - `PPV-`, `PPV_`, `PPV` 後直接接數字
  - `FC2-PPV`, `FC2_PPV` 等變體
- 大幅減少無效的網路請求，提升執行效率
