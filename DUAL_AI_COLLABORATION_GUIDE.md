# Claude Code + GitHub Copilot 協作流程指南
*雙 AI 協作開發策略 - 2025年1月18日*

## 🎯 角色分工策略

### Claude Code 專責領域
- **程式碼重構** - 大型架構調整
- **核心邏輯撰寫** - 複雜演算法實作  
- **錯誤修正** - 深度除錯與最佳化
- **專案規劃** - 整體架構設計

### GitHub Copilot 專責領域  
- **程式碼補全** - 自動補全程式碼片段
- **註釋生成** - 自動生成函式和類別註釋
- **單元測試** - 自動生成測試程式碼
- **文件撰寫** - README、API 文件等

## 🔄 同步協作流程

### 工作流程 A: 重構導向 (Claude Code 先行)

#### 第 1 階段: Claude Code 重構
```
1. 使用 Claude Code 進行程式碼重構
   - 專注於架構調整
   - 核心邏輯優化  
   - 不添加詳細註釋 (留給 Copilot)

2. 提交到 Git
   git add .
   git commit -m "refactor: 核心邏輯重構 - 待添加註釋"
```

#### 第 2 階段: GitHub Copilot 補強
```
1. 開啟 Copilot
2. 逐檔案添加註釋
   - 在函式上方按 Enter，讓 Copilot 生成註釋
   - 使用 /// 或 /** 觸發文件註釋
   
3. 生成測試程式碼
   - 建立 test_*.py 檔案
   - 讓 Copilot 自動生成測試用例

4. 提交完整版本
   git add .
   git commit -m "docs: 添加 Copilot 生成的註釋和測試"
```

### 工作流程 B: 文件導向 (Copilot 先行)

#### 第 1 階段: GitHub Copilot 框架
```
1. 建立檔案結構和基本註釋
2. 使用 Copilot 生成函式簽名和文件字串
3. 建立 TODO 註釋標記待實作功能
```

#### 第 2 階段: Claude Code 實作
```
1. 基於 Copilot 的框架和註釋
2. 實作具體邏輯
3. 進行深度最佳化
```

## 🛠️ VS Code 設定最佳化

### settings.json 設定
```json
{
  // Claude Code 設定
  "claude.autoComplete": true,
  "claude.contextLines": 100,
  
  // GitHub Copilot 設定  
  "github.copilot.enable": {
    "*": true,
    "plaintext": false,
    "markdown": true,
    "scminput": false
  },
  "github.copilot.editor.enableAutoCompletions": true,
  
  // 協作設定
  "editor.inlineSuggest.enabled": true,
  "editor.quickSuggestions": {
    "other": true,
    "comments": true,
    "strings": true
  },
  
  // Git 自動暫存 (便於切換)
  "git.enableSmartCommit": true,
  "git.autofetch": true
}
```

### 快捷鍵設定 (keybindings.json)
```json
[
  {
    "key": "ctrl+alt+p",
    "command": "workbench.panel.chat.view.copilot.focus",
    "when": "!chatSessionRequestInProgress"
  },
  {
    "key": "ctrl+shift+space",
    "command": "github.copilot.generate",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+/",
    "command": "github.copilot.generateDocs", 
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+alt+c",
    "command": "workbench.action.chat.open",
    "when": "!chatSessionRequestInProgress"
  },
  {
    "key": "ctrl+alt+enter",
    "command": "inlineChat.start",
    "when": "editorFocus"
  }
]
```

## 📋 具體操作範例

### 範例 1: 新功能開發

#### Step 1: Claude Code 重構 (5分鐘)
```python
# 由 Claude Code 生成核心邏輯
class ActressSearchEngine:
    def __init__(self, config):
        self.config = config
        self.sources = []
    
    def search_actress_info(self, name):
        results = []
        for source in self.sources:
            result = source.search(name)
            if result:
                results.append(result)
        return self.merge_results(results)
    
    def merge_results(self, results):
        # 複雜的合併邏輯
        pass
```

#### Step 2: GitHub Copilot 註釋 (3分鐘)
```python
class ActressSearchEngine:
    """
    Actress information search engine that aggregates results from multiple sources.
    
    This class provides a unified interface to search for actress information
    across different data sources and intelligently merges the results.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the search engine with configuration.
        
        Args:
            config: Configuration dictionary containing search parameters
        """
        self.config = config
        self.sources = []
    
    def search_actress_info(self, name: str) -> List[Dict[str, Any]]:
        """
        Search for actress information across all configured sources.
        
        Args:
            name: The name of the actress to search for
            
        Returns:
            List of search results from all sources
        """
        # ...existing code...
```

### 範例 2: 文件生成

#### Step 1: Copilot 生成 README 框架
```markdown
# 女優分類系統

## 功能特色
- [ ] 自動分類功能
- [ ] 智慧搜尋功能  
- [ ] 片商識別功能

## 安裝說明
```

#### Step 2: Claude Code 完善內容
```markdown
# 女優分類系統

企業級的女優影片自動分類與管理系統，支援多來源資料整合、智慧分類演算法、片商識別等功能。

## 功能特色
- ✅ **自動分類功能** - 基於女優姓名智慧分類影片檔案
- ✅ **智慧搜尋功能** - 多來源整合搜尋 (AV-WIKI, Chiba-F.net)
- ✅ **片商識別功能** - 自動識別並分類主要片商作品

## 系統架構
...詳細技術說明...
```

## 🔄 同步確保機制

### 1. Git 工作流程
```bash
# 建立功能分支
git checkout -b feature/actress-search

# Claude Code 階段
git add .
git commit -m "feat: 實作核心搜尋邏輯 (待文件)"

# GitHub Copilot 階段  
git add .
git commit -m "docs: 添加註釋和文件 (Copilot)"

# 合併到主分支
git checkout main
git merge feature/actress-search
```

### 2. 任務追蹤標記
```python
# TODO: [COPILOT] 需要添加詳細註釋
# TODO: [COPILOT] 需要生成單元測試
# DONE: [CLAUDE] 核心邏輯已完成
```

### 3. 檔案狀態標記
```
src/
├── models/
│   ├── actress.py          # ✅ Claude + ✅ Copilot  
│   ├── database.py         # ✅ Claude + ⏳ Copilot
│   └── search_engine.py    # ⏳ Claude + ❌ Copilot
```

## 🎯 最佳實踐建議

### 時間分配建議
```
總開發時間 100%
├── Claude Code 60%  (重構、核心邏輯)
├── Copilot 30%      (註釋、文件、測試)  
└── 手動調整 10%     (整合、調優)
```

### 品質控制檢查點
1. **Claude Code 完成後**
   - [ ] 核心功能運作正常
   - [ ] 程式碼結構清晰
   - [ ] 錯誤處理完整

2. **Copilot 完成後**  
   - [ ] 所有函式都有註釋
   - [ ] API 文件完整
   - [ ] 測試覆蓋率足夠

3. **最終整合檢查**
   - [ ] 註釋與程式碼一致
   - [ ] 文件與實作同步
   - [ ] 測試全部通過

## 💰 成本效益分析

### Token 使用最佳化
```
Claude Code:
- 專注於程式碼生成 (輸出 Token 較多)
- 減少註釋請求 (節省輸入 Token)

GitHub Copilot:  
- 月費制註釋生成 (無 Token 限制)
- 自動補全減少手動輸入

預估節省: 40-50% 的 Claude Token 使用量
```

### 開發效率提升
```
傳統方式: 100% 時間
Claude Code Only: 80% 時間  
雙 AI 協作: 60% 時間

效率提升: 40%
```

## 🚀 立即行動計畫

### Week 1: 環境設定
1. 配置 VS Code 設定檔
2. 設定 Git 工作流程
3. 建立專案模板

### Week 2-3: 流程調校
1. 小專案測試協作流程
2. 調整分工策略
3. 最佳化 Token 使用

### Week 4+: 規模化應用
1. 應用到大型專案
2. 建立標準作業程序
3. 持續最佳化流程

## 🎮 修正後的快捷鍵說明

**重要**: 原本的 `Ctrl+Shift+C` 與 Windows 系統快捷鍵衝突，已修正為：

### 新的快捷鍵配置
- **Ctrl+Alt+P** → 開啟 GitHub Copilot 面板
- **Ctrl+Alt+C** → 開啟 Claude Code 聊天
- **Ctrl+Shift+Space** → GitHub Copilot 生成程式碼
- **Ctrl+Shift+/** → GitHub Copilot 生成註釋
- **Ctrl+Alt+Enter** → 啟動內聯聊天 (Inline Chat)

### 使用方式
1. **重新啟動 VS Code** 載入新的快捷鍵設定
2. **測試快捷鍵** 確認功能正常
3. **如果仍有衝突** 可以在 VS Code 中按 `Ctrl+K Ctrl+S` 打開快捷鍵設定手動調整

**這個雙 AI 協作策略能讓你的開發效率最大化，同時最佳化成本！** 🎯
