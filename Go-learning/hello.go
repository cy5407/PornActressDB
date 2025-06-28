package main

import "fmt"

func main() {
	fmt.Println("Hello, World!")

	name := "john wick"
	fmt.Printf("Hello, %s,start to go!\n", name) //格式輸出

	//宣告變數
	age := 18
	height := 1.8
	weight := 70.5
	fmt.Printf("age: %d, height: %.2f, weight: %.2f\n", age, height, weight)
	//宣告常數
	const pi = 3.14
	fmt.Printf("pi: %.2f\n", pi)
	//宣告陣列
	arr := [5]int{1, 2, 3, 4, 5}
	fmt.Printf("Array: %v\n", arr)
	//宣告切片
	slice := []int{1, 2, 3, 4, 5}
	fmt.Printf("Slice: %v\n", slice)

	//計算
	killer := 100
	victim := 50
	result := killer - victim
	fmt.Printf("Result: %d\n", result)
}

// 注意：在 Go 語言中，Printf 的首字母應該是大寫的 P
// 因此應該使用 fmt.Printf 而不是 fmt.printf
