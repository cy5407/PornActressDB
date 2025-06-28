package main

import "fmt"

func main() {
	fmt.Printf("Go 控制結構學習 - if/else 語句\n")
	fmt.Printf("====================================\n")

	// 基本的 if 語句
	fmt.Println("基本的 if 語句")
	score := 85
	if score >= 60 {
		fmt.Println("及格")
	} else {
		fmt.Println("不及格")
	}
}

// 注意：在 Go 語言中，if 語句的條件表達式後面不需要括號
// 並且 else 語句是可選的。if 語句可以單獨使用，也可以與 else 語句一起使用。
// 這段程式碼展示了如何使用 if 語句來檢查分數是否及格。
