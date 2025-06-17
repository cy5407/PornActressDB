# 女優分類

## 專案描述
[請填寫專案的主要功能和目標]

## 功能特色
- [功能 1]
- [功能 2] 
- [功能 3]

## 技術架構
- **程式語言**: [請填寫]
- **框架**: [請填寫]
- **資料庫**: [請填寫]
- **部署**: [請填寫]

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
