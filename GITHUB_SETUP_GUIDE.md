# 如何建立 GitHub 專案 - 完整指引

## 🎯 建立 GitHub 儲存庫步驟

### 步驟 1: 登入 GitHub
1. 前往 [GitHub.com](https://github.com)
2. 登入您的 GitHub 帳戶

### 步驟 2: 建立新儲存庫
1. 點擊右上角的 **"+"** 按鈕
2. 選擇 **"New repository"**
3. 填寫儲存庫資訊：
   - **Repository name**: `actress-classifier` (或您偏好的名稱)
   - **Description**: `智慧影片分類管理系統 - 支援女優識別、片商分類與多源搜尋`
   - **Visibility**: 選擇 `Private` (建議) 或 `Public`
   - **不要** 勾選 "Add a README file"
   - **不要** 勾選 "Add .gitignore"
   - **不要** 勾選 "Choose a license"
4. 點擊 **"Create repository"**

### 步驟 3: 設定本地專案連接
複製 GitHub 給您的指令，通常類似：

```bash
git remote add origin https://github.com/YOUR_USERNAME/actress-classifier.git
git branch -M main
git push -u origin main
```

## 🚀 自動化腳本

我為您準備了自動化腳本，請按照以下步驟執行：

### 1. 準備推送腳本
執行以下命令（請將 YOUR_USERNAME 和 REPOSITORY_NAME 替換為實際值）：

```powershell
# 設定您的 GitHub 使用者名稱和儲存庫名稱
$USERNAME = "YOUR_USERNAME"
$REPO_NAME = "actress-classifier"

# 添加遠端儲存庫
git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"

# 重命名主分支為 main
git branch -M main

# 推送到 GitHub
git push -u origin main
```

### 2. 如果您想要不同的儲存庫名稱
只需修改上面的 `$REPO_NAME` 變數即可。

## 📋 推送前檢查清單

在推送到 GitHub 前，請確認：

- [x] ✅ 所有敏感資料已在 .gitignore 中排除
- [x] ✅ 資料庫檔案 (*.db) 已被正確忽略
- [x] ✅ 虛擬環境 (venv/) 已被忽略
- [x] ✅ README.md 檔案已準備好
- [x] ✅ LICENSE 檔案已包含
- [x] ✅ 所有必要檔案已提交

## 🔐 隱私與安全

### 已保護的資料
以下檔案/目錄已在 .gitignore 中排除，不會上傳到 GitHub：
- `*.db` - 資料庫檔案
- `venv/` - 虛擬環境
- `*.log` - 日誌檔案
- `.env` - 環境變數檔案

### 建議設定
1. **使用 Private Repository**: 如果包含任何敏感資訊
2. **定期檢查**: 確保沒有意外提交敏感檔案
3. **Branch Protection**: 設定 main 分支保護規則

## 🎉 完成後的驗證

推送成功後，您應該能在 GitHub 上看到：
1. 完整的專案結構
2. 美觀的 README.md 顯示
3. 所有原始碼檔案
4. 專案管理文件

## 🔧 故障排除

### 如果遇到錯誤
1. **遠端已存在**: 
   ```bash
   git remote remove origin
   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
   ```

2. **分支名稱問題**:
   ```bash
   git branch -M main
   ```

3. **推送被拒絕**:
   ```bash
   git pull origin main --allow-unrelated-histories
   git push origin main
   ```

## 📞 需要協助？

如果您在建立過程中遇到任何問題，請告訴我：
1. 錯誤訊息的完整內容
2. 您執行的具體步驟
3. 您的 GitHub 使用者名稱

我會提供更詳細的協助！
