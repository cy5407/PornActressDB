package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// 掃描本體
type VideoScanner struct {
	SupportedFormats []string
	TotalFiles       int
	VideoFiles       int
	TotalSize        int64
	ScanTime         time.Duration
}

// 掃描結果 - 每個檔案的資訊卡片
type ScanResult struct {
	FilePath string
	FileName string
	FileSize int64
	Format   string
	IsVideo  bool
}

// 建立新的掃描器
func NewVideoScanner() *VideoScanner {
	return &VideoScanner{
		SupportedFormats: []string{".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"},
		TotalFiles:       0,
		VideoFiles:       0,
		TotalSize:        0,
		ScanTime:         0,
	}
}

//檢查是否為影片檔
func (vs *VideoScanner) IsVideoFile(filePath string) bool {
		ext := strings.ToLower(filepath.Ext(filePath))
		for _, format := range vs.SupportedFormats {
			if ext == format {
				return true
			}
		}
		return false
}

// 掃描指定目錄
func (vs* VideoScanner) ScanDirectory(dir string) ([]ScanResult,error) {
	fmt.Printf("開始掃描目錄：%s
", dir)
	fmt.Printf("=====================================
")

	Starttime := time.Now()
	var results []ScanResult

	//檢查目錄是否存在
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		return nil, fmt.Errorf("目錄不存在：%s", dir)
}

//重置計數器
	vs.TotalFiles = 0
	vs.VideoFiles = 0
	vs.TotalSize = 0

// 遍歷目錄
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			fmt.Printf("錯誤：無法訪問檔案 %s: %v
", path, err)
			return nil // 繼續處理其他檔案
		}

		//跳過目錄，只處理檔案
		if info.IsDir() {
			return nil
		}
	}

//更新統計
vs.TotalFiles++
FileName := info.Name()
FileExt := strings.ToLower(FilePath.Ext(FileName))
IsVideo := vs.IsVideoFile(filename)

		if IsVideo {
			vs.VideoFiles++
			vs.TotalSize += info.Size()
			fmt.Printf("找到影片檔案：%s (%d bytes)
", path, info.Size())
		}else {
			fmt.Printf("找到非影片檔案：%s (%d bytes)
", path, info.Size())
		}

// 建立掃描結果
		result := ScanResult{
			FilePath: path,
			FileName: FileName,
			FileSize: info.Size(),
			Format:   FileExt,
			IsVideo:  IsVideo,
		}

		results = append(results, result)
		return nil // 繼續處理其他檔案
	}

	//格式化檔案大小
	




func main() {
	fmt.Printf("Go語言影片檔案掃描器 v1.0
")
	fmt.Printf("語言結構定義完成
")
	fmt.Printf("效能優化測試中...
")

	Scanner := VideoScanner{
		SupportedFormats: []string{"mp4", "avi", "mkv"},
		TotalFiles:       0,
		VideoFiles:       0,
		TotalSize:        0,
		ScanTime:         0,
	}

	fmt.Printf("掃描器已初始化，支援的格式：%v
", Scanner.SupportedFormats)

	result := ScanResult{
		FilePath: "example/path/to/video.mp4",
		FileName: "video.mp4",
		FileSize: 1024000,
		Format:   "mp4",
		IsVideo:  true,
	}

	// ✅ 完整的輸出語句
	fmt.Printf("📝 掃描結果：
")
	fmt.Printf("   檔案路徑：%s
", result.FilePath)
	fmt.Printf("   檔名：%s
", result.FileName)
	fmt.Printf("   檔案大小：%d bytes
", result.FileSize)
	fmt.Printf("   格式：%s
", result.Format)
	fmt.Printf("   是否為影片：%t
", result.IsVideo)

	// 額外示範：計算檔案大小的人類可讀格式
	sizeInMB := float64(result.FileSize) / 1024 / 1024
	fmt.Printf("   檔案大小：%.2f MB
", sizeInMB)

	fmt.Printf("
🎉 程式執行完成！
")
	fmt.Printf("====================================
")
}

// 注意：這段程式碼是 Go 語言的基本結構，並不包含實際的檔案掃描邏輯。
// 實際的檔案掃描邏輯需要使用 Go 的檔案系統相關套件，如 os 和 filepath。
// 這段程式碼主要展示了如何定義結構體、初始化結構體實例，並輸出相關資訊。
// 你可以根據需要擴展這個程式碼，加入實際
// 的檔案掃描邏輯和其他功能。