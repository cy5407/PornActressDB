#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專案結構自動初始化工具
用於建立標準化的專案目錄結構，包含英文目錄和中文說明檔
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ProjectInitializer:
    """專案結構初始化工具"""
    
    def __init__(self, project_name: str, project_path: Optional[str] = None):
        """初始化工具
        
        Args:
            project_name: 專案名稱
            project_path: 專案路徑，預設為當前目錄下的專案名稱
        """
        self.project_name = project_name
        self.project_path = Path(project_path or f"./{project_name}")
        self.today = datetime.now().strftime("%Y-%m-%d")
        
    def create_directory_structure(self) -> None:
        """建立標準目錄結構"""
        directories = [
            "src",
            "src/models",
            "src/services", 
            "src/utils",
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/fixtures",
            ".ai-playground",
            ".ai-playground/experiments",
            ".ai-playground/validations",
            ".ai-playground/prototypes", 
            ".ai-playground/archived",
            "docs",
            "docs/api",
            "docs/guides",
            "config",
            "scripts",
            "專案管理",
            "專案管理/需求規格",
            "專案管理/會議記錄",
            "專案管理/進度報告",
            "專案管理/專案計畫",
            ".vscode",
            ".github",
            ".github/workflows",
            ".github/personal"
        ]
        
        print(f"📁 建立目錄結構...")
        for directory in directories:
            dir_path = self.project_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {directory}/")
    
    def create_description_files(self) -> None:
        """建立中文說明檔"""
        descriptions = {
            "src/主要程式碼.txt": """專案主要程式碼區域

用途說明：
- 存放核心業務邏輯
- 主要功能模組
- 資料處理相關程式

目錄結構：
- models/     : 資料模型定義
- services/   : 業務邏輯服務
- utils/      : 工具函式
- main.py     : 程式入口點

最後更新：{date}
維護人員：[請填寫您的名字]
相關檔案：main.py""",

            "tests/測試程式說明.txt": """正式測試程式區域

用途說明：
- 單元測試
- 整合測試
- 測試資料和固定裝置

測試架構：
- unit/        : 單元測試
- integration/ : 整合測試  
- fixtures/    : 測試資料

執行方式：
pytest tests/

最後更新：{date}
測試覆蓋率目標：85% 以上""",

            ".ai-playground/AI實驗區說明.txt": """AI Agent 實驗和測試區域

用途說明：
- AI Agent 產生的實驗性程式碼
- 功能驗證和原型測試
- 臨時除錯程式

使用規則：
- 所有 AI 產生的測試檔案放在這裡
- 完成驗證後移動到 archived/ 目錄
- 檔案命名使用時間戳記格式

子目錄說明：
- experiments/ : 實驗性程式碼
- validations/ : 功能驗證檔案
- prototypes/  : 原型測試
- archived/    : 已完成的測試

最後更新：{date}
注意事項：此目錄會被 .gitignore 部分忽略""",

            ".ai-playground/experiments/實驗程式碼說明.txt": """實驗性程式碼區域

用途：
- AI Agent 產生的實驗程式
- 新功能原型驗證
- 概念驗證程式碼

檔案命名格式：
experiment_YYYYMMDD_功能描述.py

範例：
experiment_20250616_user_auth.py
experiment_20250616_api_test.py

最後更新：{date}""",

            ".ai-playground/validations/驗證程式說明.txt": """功能驗證檔案區域

用途：
- 驗證現有功能正確性
- 測試程式碼邏輯
- 確認 API 回應

檔案命名格式：
validation_YYYYMMDD_測試目標.py

範例：
validation_20250616_login_api.py
validation_20250616_database_connection.py

最後更新：{date}""",

            ".ai-playground/prototypes/原型程式說明.txt": """原型測試區域

用途：
- 新功能原型開發
- 技術可行性驗證
- 使用者介面雛形

檔案命名格式：
prototype_YYYYMMDD_原型名稱.py

範例：
prototype_20250616_new_dashboard.py
prototype_20250616_chat_feature.py

最後更新：{date}""",

            ".ai-playground/archived/歸檔檔案說明.txt": """已完成測試歸檔區

用途：
- 已驗證完成的實驗檔案
- 成功整合到主專案的程式碼
- 保留作為參考的測試程式

管理方式：
- 定期清理超過 30 天的檔案
- 重要的實驗結果永久保留
- 按月份建立子目錄整理

最後更新：{date}""",

            "docs/專案文件說明.txt": """專案文件區域

用途說明：
- API 文件
- 使用指南
- 技術說明

目錄結構：
- api/      : API 相關文件
- guides/   : 使用指南
- README.md : 專案總覽

文件格式：主要使用 Markdown 格式
最後更新：{date}""",

            "config/設定檔說明.txt": """設定檔案區域

用途說明：
- 不同環境的設定檔
- 應用程式組態
- 部署相關設定

環境分類：
- development.yml : 開發環境
- testing.yml     : 測試環境
- production.yml  : 正式環境

最後更新：{date}
注意事項：敏感資訊請使用環境變數""",

            "scripts/工具腳本說明.txt": """工具腳本區域

用途說明：
- 專案管理腳本
- 自動化工具
- 部署腳本

常用腳本：
- setup.py          : 環境設定
- deploy.py         : 部署腳本
- manage_ai_files.py: AI 檔案管理

最後更新：{date}""",

            "專案說明.txt": f"""{self.project_name} - 專案總覽

專案名稱：{self.project_name}
建立日期：{self.today}
專案類型：[請填寫專案類型，如：Web 應用程式、API 服務等]

專案描述：
[請填寫專案的主要功能和目標]

技術架構：
- 程式語言：[請填寫主要程式語言]
- 框架：[請填寫使用的框架]
- 資料庫：[請填寫資料庫類型]

目錄結構說明：
- src/              : 主要程式碼
- tests/            : 測試程式
- .ai-playground/   : AI 實驗區
- docs/             : 專案文件
- 專案管理/         : 業務文件

團隊成員：
- [請填寫團隊成員資訊]

重要注意事項：
- 請遵循專案的程式碼風格規範
- AI 實驗檔案請放在 .ai-playground/ 目錄
- 提交程式碼前請執行測試

最後更新：{self.today}"""
        }
        
        print("📝 建立中文說明檔...")
        for file_path, content in descriptions.items():
            full_path = self.project_path / file_path
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content.format(date=self.today))
            print(f"   ✅ {file_path}")
    
    def create_gitignore(self) -> None:
        """建立 .gitignore 檔案"""
        gitignore_content = """# Python 相關
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/
pip-log.txt
pip-delete-this-directory.txt

# AI 實驗區 (部分忽略)
.ai-playground/experiments/
.ai-playground/validations/
.ai-playground/prototypes/
!.ai-playground/archived/
!.ai-playground/*.txt

# 臨時檔案
*.temp
*.tmp
debug_*
temp_*
*_backup_*

# IDE 設定
.vscode/settings.json.backup_*
.idea/
*.swp
*.swo

# 作業系統檔案
.DS_Store
Thumbs.db
ehthumbs.db
Desktop.ini

# 環境設定
.env
.env.local
.env.*.local
.env.development
.env.production

# 建構輸出
dist/
build/
*.egg-info/
.eggs/

# 日誌檔案
*.log
logs/
log/

# 測試相關
.coverage
.pytest_cache/
.tox/
htmlcov/
.cache

# Node.js (如果有前端)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 資料庫
*.db
*.sqlite
*.sqlite3

# 文件建構
_build/
"""
        
        gitignore_path = self.project_path / ".gitignore"
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("📄 建立 .gitignore")
    
    def create_vscode_settings(self) -> None:
        """建立 VS Code 設定檔"""
        settings = {
            "files.associations": {
                "*.txt": "plaintext"
            },
            "files.encoding": "utf8",
            "files.autoGuessEncoding": True,
            "explorer.sortOrder": "type",
            "explorer.fileNesting.enabled": True,
            "explorer.fileNesting.patterns": {
                "*.txt": "",
                "README.md": "*.md"
            },
            "python.defaultInterpreterPath": "./venv/bin/python",
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": ["tests/"],
            
            # GitHub Copilot 最佳化設定
            "github.copilot.enable": True,
            "github.copilot.editor.enableCodeActions": True,
            "github.copilot.renameSuggestions.triggerAutomatically": True,
            "window.commandCenter": True,
            "chat.commandCenter.enabled": True,
            "workbench.commandPalette.experimental.askChatLocation": "chatView",
            "github.copilot.chat.search.semanticTextResults": True,
            "github.copilot.nextEditSuggestions.enabled": True,
            "editor.inlineSuggest.edits.showCollapsed": True,
            
            # Copilot Chat 設定
            "github.copilot.chat.followUps": "firstOnly",
            "github.copilot.chat.localeOverride": "zh-TW",
            "github.copilot.chat.useProjectTemplates": True,
            "github.copilot.chat.scopeSelection": True,
            "chat.detectParticipant.enabled": False,
            "chat.promptFiles": True,
            "chat.promptFilesLocations": {
                ".github/personal": True
            },
            "github.copilot.chat.languageContext.typescript.enabled": True,
            "github.copilot.chat.agent.thinkingTool": True,
            
            # 內容感知優化
            "github.copilot.chat.editor.temporalContext.enabled": True,
            "github.copilot.chat.codesearch.enabled": True,
            
            # 編輯確認機制
            "chat.editing.confirmEditRequestRemoval": True,
            "chat.editing.confirmEditRequestRetry": True,
            "inlineChat.finishOnType": False,
            
            # Agent 模式設定
            "chat.agent.enabled": True,
            "chat.agent.maxRequests": 75,
            "telemetry.telemetryLevel": "off",
            
            # 語音設定
            "accessibility.voice.speechLanguage": "zh-TW",
            "accessibility.voice.autoSynthesize": "off",
            "accessibility.voice.keywordActivation": "off",
            "accessibility.voice.speechTimeout": 5000,
            "accessibility.voice.ignoreCodeBlocks": True
        }
        
        tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "整理 AI 實驗檔案",
                    "type": "shell",
                    "command": "python",
                    "args": ["scripts/manage_ai_files.py", "--organize"],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always"
                    }
                },
                {
                    "label": "執行測試",
                    "type": "shell", 
                    "command": "pytest",
                    "args": ["tests/", "-v"],
                    "group": "test"
                },
                {
                    "label": "產生專案報告",
                    "type": "shell",
                    "command": "python", 
                    "args": ["scripts/generate_project_summary.py"],
                    "group": "build"
                }
            ]
        }
        
        vscode_dir = self.project_path / ".vscode"
        
        # 建立 settings.json
        settings_path = vscode_dir / "settings.json"
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        # 建立 tasks.json  
        tasks_path = vscode_dir / "tasks.json"
        with open(tasks_path, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
            
        print("⚙️  建立 VS Code 設定檔")
    
    def create_copilot_instructions(self) -> None:
        """建立 GitHub Copilot 指令檔案"""
        instructions = {
            ".github/.copilot-instructions.md": f"""# {self.project_name} - GitHub Copilot 專案指令

## 專案資訊
- 專案名稱：{self.project_name}
- 建立日期：{self.today}
- 程式語言：Python (請根據實際情況調整)

## 一般指令
- 請使用繁體中文 (zh-TW) 回應
- 程式碼註解請使用繁體中文
- 變數命名使用有意義的英文名稱
- 遵循 PEP 8 程式碼風格指南

## 檔案管理規則
- 所有 AI 實驗檔案放在 .ai-playground/ 目錄下
- 使用時間戳記命名：experiment_YYYYMMDD_描述.py
- 每個檔案開頭加入用途說明註解
- 完成驗證後移動到 archived/ 目錄

## 目錄結構規範
- src/：主要程式碼，需要產生對應的測試檔案
- tests/：正式測試，使用 pytest 框架
- .ai-playground/：實驗區，暫時性檔案
- docs/：技術文件，使用 Markdown 格式

## 程式碼品質要求
- 使用 type hints
- 函式需要完整的 docstring
- 適當的例外處理
- 避免硬編碼敏感資訊

## 資訊安全考量
- 設定檔使用環境變數
- API 金鑰等敏感資訊不可硬編碼
- 輸入驗證和清理
- 遵循安全程式碼實務""",
            
            ".github/.copilot-test-instructions.md": """# 測試產生指令

## 測試架構
- 使用 pytest 作為主要測試框架
- 測試檔案命名為 test_*.py
- 將相關測試組織在同一個測試套件中

## 測試內容要求
- 包含正常情況和邊界條件的測試
- 測試應該獨立且可重複執行
- 使用有意義的測試函式名稱
- 包含適當的斷言和錯誤訊息
- 測試覆蓋率目標：85% 以上

## 測試檔案結構
```python
import pytest
from src.module import function_to_test

class TestFunctionName:
    \"\"\"測試 function_name 函式\"\"\"
    
    def test_normal_case(self):
        \"\"\"測試正常情況\"\"\"
        pass
        
    def test_edge_case(self):
        \"\"\"測試邊界條件\"\"\"
        pass
        
    def test_error_handling(self):
        \"\"\"測試錯誤處理\"\"\"
        pass
```""",
            
            ".github/.copilot-review-instructions.md": """# 程式碼審查指令

## 審查重點
- 檢查程式碼邏輯和演算法正確性
- 驗證資訊安全最佳實務
- 確認程式碼可讀性和維護性
- 檢查效能和資源使用
- 確認遵循專案編碼規範

## 回饋格式
- 使用繁體中文提供回饋
- 分類問題優先順序（高/中/低）
- 提供具體的改善建議
- 包含程式碼範例說明

## 審查檢查清單
- [ ] 函式和變數命名是否清楚
- [ ] 是否有適當的錯誤處理
- [ ] 是否有安全性漏洞
- [ ] 效能是否可以優化
- [ ] 測試覆蓋率是否足夠""",
            
            ".github/.copilot-commit-message-instructions.md": """# 提交訊息產生指令

## 格式規範
- 使用繁體中文撰寫提交訊息
- 第一行：簡短描述（50字以內）
- 空一行後：詳細說明（如需要）
- 最後加上相關的 issue 編號（如有）

## 類型前綴
- feat: 新功能
- fix: 修復錯誤
- docs: 文件更新
- style: 程式碼格式調整
- refactor: 重構程式碼
- test: 測試相關
- chore: 其他維護工作
- ai-experiment: AI 實驗相關

## 範例格式
```
feat: 新增使用者認證功能

- 實作 JWT 令牌驗證
- 加入登入/登出 API 端點
- 新增使用者權限檢查中介軟體

相關 Issue: #123
```""",
            
            ".github/.copilot-pull-request-description-instructions.md": """# Pull Request 描述產生指令

## 結構要求
- 使用繁體中文撰寫
- 包含變更摘要
- 列出主要變更項目
- 說明測試方法（如適用）
- 包含螢幕截圖（如為 UI 變更）

## 範本格式
```markdown
## 變更摘要
[簡短描述這個 PR 的主要目的]

## 主要變更
- [ ] 變更項目 1
- [ ] 變更項目 2
- [ ] 變更項目 3

## 測試說明
- [ ] 單元測試已通過
- [ ] 整合測試已通過
- [ ] 手動測試已完成

## 檢查清單
- [ ] 程式碼已經過測試
- [ ] 文件已更新
- [ ] 遵循程式碼風格指南
- [ ] 沒有機敏資訊外洩
- [ ] AI 實驗檔案已適當整理
```

## 注意事項
- 確保說明足夠詳細，讓審查者理解變更內容
- 如有破壞性變更，請特別標註
- 包含相關的 issue 或票證編號"""
        }
        
        print("🤖 建立 GitHub Copilot 指令檔案...")
        for file_path, content in instructions.items():
            full_path = self.project_path / file_path
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ {file_path}")
    
    def create_readme(self) -> None:
        """建立 README.md 檔案"""
        readme_content = f"""# {self.project_name}

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
cd {self.project_name}

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\\Scripts\\activate     # Windows

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
{self.project_name}/
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
- v1.0.0 - 初始版本 ({self.today})

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
"""
        
        readme_path = self.project_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("📖 建立 README.md")
    
    def create_ai_file_manager(self) -> None:
        """建立 AI 檔案管理腳本"""
        manager_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent 測試檔案自動管理工具
用於整理和管理 .ai-playground 目錄中的檔案
"""

import argparse
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import re


class AIFileManager:
    """AI 檔案管理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.playground_dir = self.project_root / ".ai-playground"
    
    def organize_files(self):
        """整理散落的測試檔案"""
        print("🔄 開始整理 AI 實驗檔案...")
        
        # 定義檔案模式和目標目錄
        patterns = {
            r"test_.*\\.py$": "validations",
            r"experiment.*\\.py$": "experiments",
            r"prototype.*\\.py$": "prototypes", 
            r"debug.*\\.py$": "experiments",
            r"temp.*\\.py$": "experiments",
            r"validation.*\\.py$": "validations"
        }
        
        moved_count = 0
        # 掃描專案根目錄和 src 目錄
        for search_dir in [self.project_root, self.project_root / "src"]:
            for file_path in search_dir.glob("*.py"):
                if self._should_move_file(file_path):
                    target_dir = self._get_target_directory(file_path, patterns)
                    if target_dir and self._move_file_safely(file_path, target_dir):
                        moved_count += 1
        
        print(f"✅ 整理完成，移動了 {moved_count} 個檔案")
    
    def clean_old_files(self, days: int = 7):
        """清理舊的測試檔案"""
        print(f"🧹 清理 {days} 天前的檔案...")
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        for file_path in self.playground_dir.rglob("*.py"):
            if file_path.parent.name == "archived":
                continue
                
            if file_path.stat().st_mtime < cutoff_date.timestamp():
                print(f"發現舊檔案: {file_path.relative_to(self.project_root)}")
                response = input(f"移動到 archived/ ? (y/N): ").strip().lower()
                if response == 'y':
                    archive_path = self.playground_dir / "archived" / file_path.name
                    # 避免檔名衝突
                    if archive_path.exists():
                        timestamp = datetime.now().strftime("%H%M%S")
                        archive_path = archive_path.with_stem(f"{archive_path.stem}_{timestamp}")
                    
                    shutil.move(str(file_path), str(archive_path))
                    print(f"   ✅ 已歸檔: {archive_path.relative_to(self.project_root)}")
                    cleaned_count += 1
        
        print(f"✅ 清理完成，歸檔了 {cleaned_count} 個檔案")
    
    def generate_report(self):
        """產生 AI 活動報告"""
        print("📊 產生 AI Agent 活動報告...")
        
        stats = {}
        total_files = 0
        
        for subdir in ["experiments", "validations", "prototypes", "archived"]:
            dir_path = self.playground_dir / subdir
            if dir_path.exists():
                py_files = list(dir_path.glob("*.py"))
                stats[subdir] = len(py_files)
                total_files += len(py_files)
            else:
                stats[subdir] = 0
        
        print(f"""
AI Agent 檔案統計報告
{'='*40}
📁 實驗檔案 (experiments): {stats['experiments']} 個
🔍 驗證檔案 (validations): {stats['validations']} 個  
🏗️  原型檔案 (prototypes):  {stats['prototypes']} 個
📦 歸檔檔案 (archived):    {stats['archived']} 個
{'='*40}
📈 總計: {total_files} 個 AI 產生的檔案
        """)
        
        # 分析最近活動
        recent_files = []
        week_ago = datetime.now() - timedelta(days=7)
        
        for file_path in self.playground_dir.rglob("*.py"):
            if file_path.stat().st_mtime > week_ago.timestamp():
                recent_files.append(file_path)
        
        if recent_files:
            print(f"📅 最近 7 天新增了 {len(recent_files)} 個檔案:")
            for file_path in sorted(recent_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                print(f"   • {file_path.relative_to(self.playground_dir)} ({mod_time.strftime('%m-%d %H:%M')})")
    
    def _should_move_file(self, file_path: Path) -> bool:
        """判斷檔案是否應該移動"""
        # 不移動主要程式檔案
        if file_path.name in ["main.py", "__init__.py", "setup.py"]:
            return False
        
        # 不移動已經在正確位置的檔案
        if ".ai-playground" in str(file_path):
            return False
            
        return True
    
    def _get_target_directory(self, file_path: Path, patterns: dict) -> str:
        """根據檔案名稱決定目標目錄"""
        filename = file_path.name
        
        for pattern, target_dir in patterns.items():
            if re.search(pattern, filename):
                return target_dir
        
        # 預設放到 experiments
        return "experiments"
    
    def _move_file_safely(self, file_path: Path, target_dir: str) -> bool:
        """安全地移動檔案"""
        target_path = self.playground_dir / target_dir / file_path.name
        
        # 檢查目標檔案是否已存在
        if target_path.exists():
            timestamp = datetime.now().strftime("%H%M%S")
            target_path = target_path.with_stem(f"{target_path.stem}_{timestamp}")
        
        try:
            shutil.move(str(file_path), str(target_path))
            print(f"   📁 {file_path.name} → {target_dir}/")
            return True
        except Exception as e:
            print(f"   ❌ 移動失敗 {file_path.name}: {e}")
            return False


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description="AI Agent 檔案管理工具")
    parser.add_argument("--organize", action="store_true", help="整理散落的檔案")
    parser.add_argument("--clean", action="store_true", help="清理舊檔案")
    parser.add_argument("--days", type=int, default=7, help="清理幾天前的檔案 (預設: 7)")
    parser.add_argument("--report", action="store_true", help="產生活動報告")
    parser.add_argument("--all", action="store_true", help="執行所有操作")
    
    args = parser.parse_args()
    
    if not any([args.organize, args.clean, args.report, args.all]):
        parser.print_help()
        return
    
    manager = AIFileManager()
    
    if args.all or args.organize:
        manager.organize_files()
    
    if args.all or args.clean:
        manager.clean_old_files(args.days)
    
    if args.all or args.report:
        manager.generate_report()
    
    print("\\n🎉 AI 檔案管理完成！")


if __name__ == "__main__":
    main()
'''
        
        script_path = self.project_path / "scripts" / "manage_ai_files.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(manager_script)
        script_path.chmod(0o755)  # 設定執行權限
        print("🛠️  建立 AI 檔案管理腳本")
    
    def create_requirements_txt(self) -> None:
        """建立基本的 requirements.txt"""
        requirements = """# 基本相依套件
# 請根據專案需求調整

# 測試相關
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0

# 程式碼品質
black>=23.0.0
flake8>=6.0.0
isort>=5.12.0

# 環境設定
python-dotenv>=1.0.0

# 如果是 Web 專案，請取消註解以下套件
# flask>=2.3.0
# fastapi>=0.100.0
# django>=4.2.0

# 如果需要資料庫，請取消註解以下套件
# sqlalchemy>=2.0.0
# psycopg2-binary>=2.9.0
# pymongo>=4.4.0

# 如果需要 HTTP 請求，請取消註解以下套件
# requests>=2.31.0
# httpx>=0.24.0

# 如果需要資料處理，請取消註解以下套件
# pandas>=2.0.0
# numpy>=1.24.0
# matplotlib>=3.7.0
"""
        
        req_path = self.project_path / "requirements.txt"
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write(requirements)
        print("📦 建立 requirements.txt")
    
    def initialize_project(self) -> None:
        """執行完整的專案初始化"""
        print(f"🚀 開始初始化專案: {self.project_name}")
        print(f"📍 專案路徑: {self.project_path.absolute()}")
        
        # 建立專案根目錄
        self.project_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # 執行各項初始化任務
            self.create_directory_structure()
            self.create_description_files()
            self.create_gitignore()
            self.create_vscode_settings()
            self.create_copilot_instructions()
            self.create_readme()
            self.create_ai_file_manager()
            self.create_requirements_txt()
            
            print(f"\n🎉 專案 '{self.project_name}' 初始化完成！")
            print("\n📋 後續步驟:")
            print("1. cd " + str(self.project_path))
            print("2. python -m venv venv")
            print("3. source venv/bin/activate  # Linux/Mac 或 venv\\Scripts\\activate  # Windows")
            print("4. pip install -r requirements.txt")
            print("5. git init")
            print("6. git add .")
            print("7. git commit -m \"feat: 初始化專案結構\"")
            print("8. 在 VS Code 中開啟專案資料夾")
            print("9. 根據需求編輯 專案說明.txt 和各目錄的說明檔")
            print("10. 開始使用 GitHub Copilot 進行開發！")
            
        except Exception as e:
            print(f"❌ 初始化過程中發生錯誤: {e}")
            raise


def main():
    """主程式"""
    print("=" * 60)
    print("🏗️  專案結構自動初始化工具")
    print("   English directories + Chinese description files")
    print("=" * 60)
    
    # 取得專案名稱
    project_name = input("\n📝 請輸入專案名稱: ").strip()
    if not project_name:
        print("❌ 專案名稱不能為空")
        return
    
    # 確認專案路徑
    default_path = f"./{project_name}"
    project_path = input(f"📁 專案路徑 (預設: {default_path}): ").strip()
    if not project_path:
        project_path = default_path
    
    # 檢查專案是否已存在
    if Path(project_path).exists() and any(Path(project_path).iterdir()):
        overwrite = input(f"⚠️  目錄 '{project_path}' 已存在且不為空，是否繼續? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ 取消初始化")
            return
    
    # 顯示即將建立的結構
    print(f"\n📋 即將建立的專案結構:")
    print(f"   專案名稱: {project_name}")
    print(f"   專案路徑: {Path(project_path).absolute()}")
    print(f"   建立日期: {datetime.now().strftime('%Y-%m-%d')}")
    
    confirm = input(f"\n✅ 確認建立專案? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消初始化")
        return
    
    # 執行初始化
    try:
        initializer = ProjectInitializer(project_name, project_path)
        initializer.initialize_project()
    except KeyboardInterrupt:
        print("\n❌ 使用者中斷操作")
    except Exception as e:
        print(f"\n❌ 初始化失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()