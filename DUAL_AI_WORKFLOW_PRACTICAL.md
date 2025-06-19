# Claude Code + GitHub Copilot 並行使用實戰指南
*無需快捷鍵的實用協作流程 - 2025年1月18日*

## 🎯 核心策略：分階段協作，避免衝突

### 基本原則
1. **不同階段使用不同 AI** - 避免同時使用造成混亂
2. **明確的任務分工** - 每個 AI 專精不同領域
3. **版本控制管理** - 用 Git 確保同步性
4. **標準化流程** - 建立可重複的工作模式

## 🔄 三種並行模式詳解

### 模式 1: 順序協作模式 (推薦)

#### 第 1 階段: Claude Code 重構期 (60% 時間)
```
專注任務:
✅ 程式碼架構重構
✅ 核心邏輯實作  
✅ 錯誤修正與最佳化
✅ 複雜演算法設計

操作方式:
1. 開啟 Claude Code (VS Code 內建聊天)
2. 關閉 Copilot 自動建議 (避免干擾)
3. 專心與 Claude 對話重構程式碼
4. 不要寫詳細註釋 (留給 Copilot)
```

#### 第 2 階段: GitHub Copilot 補強期 (30% 時間)
```
專注任務:
✅ 自動生成函式註釋
✅ 創建單元測試
✅ 撰寫 README 文件
✅ 程式碼自動補全

操作方式:
1. 暫停 Claude Code 對話
2. 開啟 Copilot 自動建議
3. 讓 Copilot 自動補完註釋和文件
4. 專心完善程式碼的文件化
```

#### 第 3 階段: 整合檢查期 (10% 時間)
```
檢查任務:
✅ 註釋與程式碼是否一致
✅ 文件是否完整
✅ 測試是否通過
✅ 整體品質控制
```

### 模式 2: 分檔案協作模式

#### 核心檔案 → Claude Code
```python
# src/models/database.py
# src/services/classifier_core.py  
# src/services/web_searcher.py

→ 這些複雜邏輯檔案用 Claude Code 重構
```

#### 工具檔案 → GitHub Copilot
```python
# tests/test_*.py
# docs/README.md
# scripts/utility_*.py

→ 這些標準化檔案讓 Copilot 生成
```

### 模式 3: 功能分工模式

#### Claude Code 負責 "創造"
- 新功能設計
- 架構重構
- 問題解決
- 邏輯優化

#### Copilot 負責 "完善"
- 註釋補全
- 文件生成
- 測試創建
- 格式統一

## 📋 具體操作流程 (無快捷鍵版本)

### Step 1: Claude Code 階段

#### 1.1 開啟 Claude Code
```
方式 1: VS Code 側邊欄點擊聊天圖示
方式 2: 命令面板 (F1) → 輸入 "chat"
方式 3: 直接在 VS Code 右上角點擊 Claude 圖示
```

#### 1.2 暫時關閉 Copilot (避免干擾)
```
VS Code 設定 → 搜尋 "copilot" → 暫時關閉
或者
命令面板 → "GitHub Copilot: Disable" 
```

#### 1.3 專心重構程式碼
```
與 Claude 對話範例:
"幫我重構這個女優搜尋功能，讓它支援多來源搜尋"
"優化這個分類演算法的效能"
"修正這個錯誤並加強錯誤處理"
```

#### 1.4 提交階段成果
```bash
git add .
git commit -m "refactor: Claude Code 重構核心邏輯 (待文件)"
```

### Step 2: GitHub Copilot 階段

#### 2.1 重新啟用 Copilot
```
VS Code 設定 → 啟用 GitHub Copilot
或者
命令面板 → "GitHub Copilot: Enable"
```

#### 2.2 暫停 Claude Code 對話
```
關閉 Claude 聊天視窗
或者最小化聊天面板
```

#### 2.3 讓 Copilot 補完文件
```python
# 在函式上方按 Enter，Copilot 會自動生成註釋
def search_actress_info(self, name: str):
    # 按 Enter 這裡，Copilot 會建議 docstring
    
# 在檔案開頭輸入 """, Copilot 會生成模組說明
"""
# 這裡 Copilot 會建議完整的模組文件
```

#### 2.4 生成測試檔案
```python
# 建立 test_search_engine.py
# 讓 Copilot 自動生成測試用例
import pytest
# Copilot 會自動建議完整的測試結構
```

#### 2.5 提交文件化成果
```bash
git add .
git commit -m "docs: Copilot 生成註釋和測試"
```

## 🚫 避免衝突的關鍵原則

### 時間分離原則
```
❌ 錯誤: 同時開啟 Claude 對話和 Copilot 建議
✅ 正確: 一個時間只專注使用一個 AI
```

### 功能分離原則
```
❌ 錯誤: 用 Claude 寫註釋，用 Copilot 做重構
✅ 正確: Claude 專精重構，Copilot 專精文件
```

### 版本分離原則
```
❌ 錯誤: 在同一個 commit 混合兩個 AI 的成果
✅ 正確: 分別 commit Claude 和 Copilot 的貢獻
```

## 🔧 實際案例示範

### 案例：新增女優搜尋功能

#### Phase 1: Claude Code (核心開發)
```
1. 與 Claude 對話: "設計一個多來源女優搜尋引擎"
2. Claude 生成核心架構和邏輯
3. 實作搜尋演算法和錯誤處理
4. 提交: "feat: 實作多來源搜尋引擎核心邏輯"
```

#### Phase 2: GitHub Copilot (文件化)
```
1. 開啟新建立的搜尋檔案
2. 讓 Copilot 自動生成 docstring
3. 建立對應的測試檔案
4. 更新 README.md 說明新功能
5. 提交: "docs: 新增搜尋引擎文件和測試"
```

#### Phase 3: 整合檢查
```
1. 執行測試確保功能正常
2. 檢查文件是否與程式碼一致
3. 最終調整和最佳化
4. 提交: "polish: 完成搜尋功能整合"
```

## 📊 效益分析

### 時間分配建議
```
總開發時間: 100%
├── Claude Code: 60% (重構、邏輯、解決問題)
├── Copilot: 30%     (註釋、文件、測試)
└── 整合調整: 10%    (檢查、修正、最佳化)
```

### 品質控制檢查點
```
Claude Code 階段結束檢查:
□ 核心功能運作正常
□ 程式碼結構清晰
□ 錯誤處理完整

Copilot 階段結束檢查:  
□ 所有函式都有註釋
□ 文件完整且正確
□ 測試覆蓋率足夠

最終整合檢查:
□ 註釋與程式碼一致
□ 文件反映實際功能
□ 所有測試通過
```

## 🎯 成功的關鍵要素

### 1. 明確的切換時機
```
Claude → Copilot 切換時機:
✅ 核心邏輯實作完成
✅ 主要功能運作正常
✅ 準備開始文件化

Copilot → Claude 切換時機:
✅ 發現程式碼需要重構
✅ 遇到複雜的邏輯問題
✅ 需要架構調整
```

### 2. 清楚的任務界線
```
永遠不要讓兩個 AI 做同樣的事情
永遠在適當的時機切換 AI
永遠用 Git 記錄誰做了什麼
```

### 3. 標準化的工作流程
```
建立自己的標準作業程序
記錄什麼情況用哪個 AI
培養切換的直覺和習慣
```

## 🚀 立即開始使用

### 今天就可以試試:
1. **選一個小功能**開始練習這個流程
2. **先用 Claude** 寫出基本邏輯 (不寫註釋)
3. **切換到 Copilot** 讓它補完文件
4. **觀察兩者的差異**和互補性

**記住：不是技術問題，是流程問題！專注於養成好的協作習慣比設定快捷鍵更重要。** 🎯
