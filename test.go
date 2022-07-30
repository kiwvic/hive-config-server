package main

import (
	"fmt"
	"os/exec"
)

var cnt_log int

func log(str string) {
	exec.Command("logger", fmt.Sprintf("Jethash [%d] %s", cnt_log, str)).Run()
	cnt_log += 1
}

func main() {
	log("abibib")
	log("abibib2")
	log("abibib3")
}
