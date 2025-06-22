# GitHub 遠端倉庫設定指南

## 🚀 推送到 GitHub 的步驟

### 選項 A：建立新的 GitHub 倉庫

1. **在 GitHub 上建立新倉庫**
   - 前往 https://github.com
   - 點擊右上角的 "+" → "New repository"
   - 倉庫名稱建議：`actress-classification-system`
   - 描述：女優分類系統 - 智慧影片管理工具
   - 設為 Private（建議）
   - **不要**勾選 "Initialize this repository with a README"
   - 點擊 "Create repository"

2. **設定遠端倉庫並推送**
   ```bash
   # 添加遠端倉庫 (請替換 YOUR_USERNAME)
   git remote add origin https://github.com/YOUR_USERNAME/actress-classification-system.git
   
   # 推送 master 分支到遠端
   git push -u origin master
   
   # 推送當前的開發分支
   git push -u origin feature/web-scraper-refactor
   ```

### 選項 B：連接到現有的 GitHub 倉庫

如果您已經有 GitHub 倉庫：

```bash
# 添加遠端倉庫 (請提供您的倉庫 URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 推送所有分支
git push -u origin --all
```

## 📋 當前專案狀態

- **當前分支**: feature/web-scraper-refactor
- **主分支**: master (穩定版本)
- **提交數**: 5 個提交
- **專案狀態**: 檔案清理完成，準備進行爬蟲重構

## 🎯 推薦的推送策略

1. **先推送穩定的 master 分支**
2. **再推送開發中的 feature/web-scraper-refactor 分支**
3. **設定分支保護規則**（可選）

## ⚠️ 注意事項

- 確保倉庫設為 Private（專案包含敏感內容）
- 推送前確認 .gitignore 已設定正確
- 首次推送可能需要 GitHub 認證

## 🔐 認證設定

如果需要設定 GitHub 認證：

```bash
# 設定 Git 使用者資訊
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 使用 Personal Access Token 進行認證
# 在 GitHub Settings > Developer settings > Personal access tokens 建立
```

請告訴我您的 GitHub 使用者名稱，我就可以幫您完成設定！
