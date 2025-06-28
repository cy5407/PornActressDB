package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// VideoScanner 負責掃描影片檔案並收集統計數據。
// 它使用並行處理來提高效率。
type VideoScanner struct {
	SupportedFormats []string
	TotalFiles       int64
	VideoFiles       int64
	TotalSize        int64
	ScanTime         time.Duration
}

// ScanResult 儲存單一檔案的掃描結果。
type ScanResult struct {
	FilePath string
	FileName string
	FileSize int64
	Format   string
	IsVideo  bool
}

// NewVideoScanner 建立並初始化一個新的 VideoScanner。
func NewVideoScanner() *VideoScanner {
	return &VideoScanner{
		SupportedFormats: []string{".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"},
	}
}

// isVideoFile 檢查給定的檔案路徑是否為支援的影片格式。
func (vs *VideoScanner) isVideoFile(filePath string) bool {
	ext := strings.ToLower(filepath.Ext(filePath))
	for _, format := range vs.SupportedFormats {
		if ext == format {
			return true
		}
	}
	return false
}

// ScanDirectory 並行掃描指定目錄下的所有檔案。
// 它使用 goroutines 來加速遍歷過程。
func (vs *VideoScanner) ScanDirectory(dir string) ([]ScanResult, error) {
	startTime := time.Now()

	// 檢查目錄是否存在
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		return nil, fmt.Errorf("目錄不存在：%s", dir)
	}

	var results []ScanResult
	var wg sync.WaitGroup
	filePaths := make(chan string)
	resultChan := make(chan ScanResult)

	// 啟動一個 goroutine 來遍歷目錄並將檔案路徑發送到 channel
	wg.Add(1)
	go func() {
		defer wg.Done()
		defer close(filePaths)
		err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				log.Printf("警告：無法存取 %q: %v", path, err)
				return nil // 繼續處理其他檔案
			}
			if !info.IsDir() {
				filePaths <- path
			}
			return nil
		})
		if err != nil {
			log.Printf("錯誤：遍歷目錄時發生問題: %v", err)
		}
	}()

	// 啟動多個 worker goroutines 來處理檔案
	numWorkers := 4
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for path := range filePaths {
				info, err := os.Stat(path)
				if err != nil {
					log.Printf("警告：無法取得檔案資訊 %q: %v", path, err)
					continue
				}

				isVideo := vs.isVideoFile(path)
				result := ScanResult{
					FilePath: path,
					FileName: info.Name(),
					FileSize: info.Size(),
					Format:   strings.ToLower(filepath.Ext(path)),
					IsVideo:  isVideo,
				}
				resultChan <- result
			}
		}()
	}

	// 啟動一個 goroutine 在所有 worker 完成後關閉 resultChan
	go func() {
		wg.Wait()
		close(resultChan)
	}()

	// 收集所有結果
	for result := range resultChan {
		vs.TotalFiles++
		if result.IsVideo {
			vs.VideoFiles++
			vs.TotalSize += result.FileSize
		}
		results = append(results, result)
	}

	vs.ScanTime = time.Since(startTime)
	return results, nil
}

// formatBytes 將 bytes 轉換為人類可讀的格式 (KB, MB, GB)。
func formatBytes(b int64) string {
	const unit = 1024
	if b < unit {
		return fmt.Sprintf("%d B", b)
	}
	div, exp := int64(unit), 0
	for n := b / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.2f %cB", float64(b)/float64(div), "KMGTPE"[exp])
}

func main() {
	fmt.Println("🚀 Go 語言並行影片檔案掃描器 v2.0")
	fmt.Println("========================================")

	// 從命令列參數獲取掃描目錄，如果未提供則使用當前目錄
	scanDir := "."
	if len(os.Args) > 1 {
		scanDir = os.Args[1]
	}
	absPath, err := filepath.Abs(scanDir)
	if err != nil {
		log.Fatalf("錯誤：無法解析路徑 %q: %v", scanDir, err)
	}

	fmt.Printf("🔍 開始掃描目錄：%s

", absPath)

	scanner := NewVideoScanner()
	results, err := scanner.ScanDirectory(absPath)
	if err != nil {
		log.Fatalf("掃描失敗：%v", err)
	}

	// 輸出找到的影片檔案
	fmt.Println("--- 找到的影片檔案 ---")
	videoFileCount := 0
	for _, r := range results {
		if r.IsVideo {
			videoFileCount++
			fmt.Printf("✅ %s (%s)
", r.FilePath, formatBytes(r.FileSize))
		}
	}
	if videoFileCount == 0 {
		fmt.Println("沒有找到任何影片檔案。")
	}

	// 輸出最終統計報告
	fmt.Println("
--- 掃描報告 ---")
	fmt.Printf("掃描總耗時：%.2f 秒
", scanner.ScanTime.Seconds())
	fmt.Printf("掃描檔案總數：%d
", scanner.TotalFiles)
	fmt.Printf("找到影片檔案數：%d
", scanner.VideoFiles)
	fmt.Printf("影片檔案總大小：%s
", formatBytes(scanner.TotalSize))
	fmt.Println("========================================")
	fmt.Println("🎉 掃描完成！")
}
