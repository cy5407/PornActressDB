package main

import (
	"fmt"
	"time"
)

// 延遲測試結構
type PerformanceTest struct {
	TestName  string
	StartTime time.Time
	EndTime   time.Time
}

func testPerformance() {
	fmt.Println("=== Go 打字延遲測試 ===")

	// 測試結構體初始化
	test := PerformanceTest{
		TestName:  "打字延遲測試",
		StartTime: time.Now(),
	}

	// 簡單的迴圈測試
	for i := 0; i < 5; i++ {
		fmt.Printf("測試行 %d - 請觀察打字延遲\n", i+1)
		time.Sleep(100 * time.Millisecond)
	}

	test.EndTime = time.Now()
	duration := test.EndTime.Sub(test.StartTime)

	fmt.Printf("測試完成，耗時：%v\n", duration)
	fmt.Println("請在此行嘗試快速打字，觀察是否還有延遲...")
}

// 在這裡測試打字：
//
//
//
