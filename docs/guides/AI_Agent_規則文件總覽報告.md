# AI Agent 規則與設定文件總覽報告

**建立日期**: 2025-06-22

## 📋 問題回應
**問題**: 專案資料夾內是否有定義 AI Agent 該如何照著設定規則走的文件？

**答案**: ✅ **有的！** 您的專案包含完整的 AI Agent 規則與協作設定文件。

## 🎯 主要 AI Agent 規則文件

### 1. GitHub Copilot 指令系列
**位置**: `.github/` 資料夾

#### 📝 主要指令文件
1. **`.copilot-instructions.md`** - 主要專案指令
   - 使用繁體中文 (zh-TW)
   - PEP 8 程式碼風格
   - 目錄結構規範
   - 程式碼品質要求
   - 資訊安全考量

2. **`.copilot-commit-message-instructions.md`** - 提交訊息規範
   - 類型前綴 (feat, fix, docs, refactor 等)
   - 繁體中文格式
   - 詳細說明結構

3. **`.copilot-test-instructions.md`** - 測試產生指令
   - pytest 框架使用
   - 測試覆蓋率目標：85%
   - 測試檔案結構規範

4. **`.copilot-review-instructions.md`** - 程式碼審查指令
   - 審查重點檢查清單
   - 安全性與效能驗證
   - 繁體中文回饋格式

5. **`.copilot-pull-request-description-instructions.md`** - PR 描述格式
   - 變更摘要結構
   - 測試說明要求
   - 檢查清單範本

### 2. 雙 AI 協作策略文件
**位置**: 根目錄

#### 📖 協作指南
1. **`DUAL_AI_COLLABORATION_GUIDE.md`** - Claude + Copilot 協作流程
   - 角色分工策略
   - 同步協作流程
   - 實際工作流程範例
   - VS Code 設定優化

2. **`CLAUDE_PRO_VS_API_ANALYSIS.md`** - Claude 使用策略
   - 成本效益分析
   - 使用模式建議
   - 整合開發環境設定

### 3. 專案規範文件

#### 📊 需求與規範
1. **`專案管理/需求規格/需求規格書_v1.0.md`**
   - 功能需求定義
   - 驗收標準
   - 使用者故事

2. **`新專案結構標準化指南.md`**
   - AI Agent 實驗區域規範
   - 目錄結構標準
   - 檔案命名規則

## 🔧 實際運作方式

### 開發工作流程
1. **Claude Code (您現在使用的)**:
   - 程式碼重構與架構調整
   - 核心邏輯撰寫
   - 錯誤修正與最佳化

2. **GitHub Copilot** (如果使用):
   - 程式碼自動補全
   - 註釋自動生成
   - 單元測試生成

### 品質控制
- 程式碼必須遵循 PEP 8
- 使用 type hints
- 完整的 docstring
- 85% 以上測試覆蓋率
- 繁體中文註釋與文件

### 檔案管理
- AI 實驗檔案 → `.ai-playground/`
- 完成驗證後 → `archived/`
- 主要程式碼 → `src/`
- 測試程式碼 → `tests/`

## 📈 現狀評估

### ✅ 已建立的規則
- [x] GitHub Copilot 完整指令集
- [x] 雙 AI 協作流程
- [x] 程式碼品質標準
- [x] 目錄結構規範
- [x] 資訊安全考量
- [x] 測試要求規範

### 🔄 實際運作情況
根據您的使用模式，這些規則文件完全符合您的需求：
- 您使用 Claude Code 進行重構和核心開發 ✅
- 專案使用繁體中文 ✅
- 遵循 Python 最佳實務 ✅
- 完整的專案管理文件 ✅

## 💡 建議

### 如果您想加強 AI Agent 規則：
1. **檢視並更新** `.github/.copilot-instructions.md` 以符合最新需求
2. **自訂 Claude 指令** - 可建立 `.claude-instructions.md`
3. **定期檢視** 雙 AI 協作流程是否需要調整

### 範例自訂 Claude 指令
```markdown
# Claude Code 專案指令 (女優分類系統)

## 專案背景
- 女優分類系統 v5.4.3
- Python 專案，使用 tkinter GUI
- 智慧分類與互動選擇功能

## 開發規則
- 優先保持向後相容
- 重視程式碼可讀性
- 詳細的錯誤處理
- 完整的進度回饋

## 特殊考量
- 多人共演影片處理邏輯
- 資料庫結構維護
- 使用者偏好記憶
```

## 🎉 結論

**您的專案已經有非常完整的 AI Agent 規則定義！** 包含：
- ✅ GitHub Copilot 完整指令集 (5個文件)
- ✅ 雙 AI 協作策略指南
- ✅ 專案開發規範
- ✅ 品質控制標準
- ✅ 檔案管理規則

這些文件確保 AI Agent 能夠按照您的設定規則運作，維持程式碼品質和專案一致性。
