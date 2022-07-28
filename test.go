package main

import (
	"fmt"
	"time"
)

func main() {
	time.Sleep(time.Duration(5 * int(time.Second)))
	fmt.Println(123)
}
