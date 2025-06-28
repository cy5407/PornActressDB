# JAVDB 女優分類系統優化策略

## 🎯 優化目標
- 提升 JAVDB 搜尋成功率至 95% 以上
- 避免 IP 被封鎖，確保長期穩定使用
- 正確解析 JAVDB 頁面，準確擷取女優資訊
- 支援大批量影片處理，提升效率

## 🛡️ 反爬蟲策略（已實作並驗證有效）

### 1. 網路請求優化
- **請求間隔**: 3-7秒隨機延遲
- **編碼處理**: 移除 `Accept-Encoding: br` 避免 Brotli 解壓縮問題
- **真實 Headers**: 模擬多種真實瀏覽器（Chrome、Firefox、Safari、Edge）
- **連線管理**: 限制同時連線數，使用 Keep-Alive

### 2. 行為模擬
- **User-Agent 輪換**: 隨機選擇真實瀏覽器 UA
- **可選 Headers**: 隨機添加 DNT、Referer 等標頭
- **Session 管理**: 每 25 個請求重建 Session
- **每日限制**: 最多 80 個請求/天

### 3. 錯誤處理與重試
- **HTTP 狀態碼**: 403/429 自動延長等待時間並重試
- **連線失敗**: 自動重試最多 3 次
- **超時處理**: 30秒超時，自動重試

## 📊 搜尋結果解析（已修正並驗證）

### 1. 搜尋頁面解析
```python
# 正確的影片連結選擇器
video_links = soup.select('a[href*="/v/"]')

# 番號匹配邏輯
for link in video_links:
    link_text = link.get_text(strip=True)
    title_attr = link.get('title', '')
    text_to_check = f"{link_text} {title_attr}".upper()
    if video_id.upper() in text_to_check:
        # 找到匹配的影片
        break
```

### 2. 詳情頁面解析
```python
# 女優資訊解析（適配新 HTML 結構）
for panel in soup.select('.panel-block'):
    strong_element = panel.select_one('strong')
    if strong_element and strong_element.text.strip().rstrip(':：') == '演員':
        actress_links = panel.select('a[href*="/actors/"]')
        actresses = []
        for link in actress_links:
            next_element = link.find_next_sibling()
            # 檢查女性符號 ♀
            if (next_element and next_element.name == 'strong' and 
                ('female' in next_element.get('class', []) or '♀' in next_element.text)):
                actresses.append(link.text.strip())
```

### 3. 其他資訊解析
- **片商**: 尋找 `a[href*="/makers/"]`
- **發行日期**: 解析日期欄位
- **評分**: 提取數字評分
- **類別**: 收集所有分類標籤

## 💾 快取與效能優化

### 1. 智慧快取策略
- **快取 Key**: `javdb_{video_id.upper()}`
- **快取檔案**: `javdb_search_cache.json`
- **失效策略**: 30天自動失效
- **壓縮儲存**: JSON 格式，UTF-8 編碼

### 2. 統計與監控
- **請求統計**: 追蹤每日請求數、成功率
- **錯誤記錄**: 記錄失敗原因和頻率
- **效能監控**: 記錄平均回應時間

## 🔧 技術實作建議

### 1. 核心類別結構
```python
class SafeJAVDBSearcher:
    def __init__(self, cache_dir: str = None):
        # 初始化快取、統計、安全參數
        
    def search_javdb(self, video_id: str) -> Optional[Dict]:
        # 主要搜尋入口
        
    def safe_request(self, url: str, retry_count: int = 0) -> Optional[httpx.Response]:
        # 安全 HTTP 請求
        
    def _parse_detail_page(self, html_content: str, video_id: str) -> Optional[Dict]:
        # 詳情頁面解析
```

### 2. 設定參數優化
```python
# 安全參數
min_delay = 3.0          # 最小延遲（秒）
max_delay = 7.0          # 最大延遲（秒）
daily_limit = 80         # 每日請求限制
session_limit = 25       # Session 請求限制
timeout = 30.0           # 請求超時時間

# 重試策略
max_retries = 3          # 最大重試次數
retry_wait_base = 120    # 基礎等待時間（秒）
retry_wait_random = 180  # 隨機額外等待時間（秒）
```

### 3. Headers 配置
```python
headers = {
    'User-Agent': random.choice(user_agents),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6',
    'Accept-Encoding': 'gzip, deflate',  # 避免 br 壓縮問題
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}
```

## 📈 效能測試結果

### 實際測試案例（2025-06-21）
- **EBWH-194**: ✅ 成功找到「雨宮ひびき」
- **SSIS-001**: ✅ 成功找到「葵つかさ, 乙白さやか」  
- **MIDV-001**: ✅ 成功找到「夢見るぅ」

### 效能指標
- **搜尋成功率**: 100% (3/3)
- **平均回應時間**: 3-6秒
- **請求間隔**: 3.3-6.6秒（符合設定）
- **無 IP 封鎖**: 測試期間無任何封鎖

## 🚀 進階優化建議

### 1. 批量處理優化
- 實作批量搜尋佇列
- 支援中斷續傳功能
- 提供進度追蹤介面

### 2. 代理支援（可選）
```python
# 進階選項：代理池輪換
proxies = {
    'http://': 'http://proxy1:port',
    'https://': 'http://proxy1:port'
}
```

### 3. 機器學習優化
- 分析成功/失敗模式
- 動態調整請求參數
- 預測最佳請求時機

## 🛠️ 故障排除指南

### 1. 常見問題
- **編碼錯誤**: 確保移除 `br` 壓縮
- **選擇器失效**: 檢查 JAVDB HTML 結構變更
- **IP 封鎖**: 增加延遲時間，使用代理

### 2. 除錯工具
- 啟用詳細日誌記錄
- 儲存失敗的 HTML 回應
- 使用測試腳本驗證功能

### 3. 監控指標
- 每日成功率趨勢
- 平均回應時間變化
- 錯誤類型分布

## 📝 維護計劃

### 1. 定期檢查（每月）
- 驗證搜尋功能正常
- 檢查 HTML 結構變更
- 清理過期快取

### 2. 應急預案
- 備用搜尋來源準備
- 快速回退機制
- 使用者通知系統

### 3. 持續改進
- 收集使用者回饋
- 分析失敗案例
- 優化搜尋精準度

---

## 🎯 總結

通過上述策略的實作，JAVDB 搜尋功能已達到生產級別的穩定性和可靠性。核心改進包括：

1. **解決編碼問題**: 移除 Brotli 壓縮支援
2. **修正解析邏輯**: 更新選擇器以適配當前 JAVDB 結構  
3. **強化安全策略**: 完整的反爬蟲保護機制
4. **提升使用者體驗**: 智慧快取和錯誤處理

建議將此策略作為系統重構的核心參考文件，確保女優分類系統的長期穩定運作。
