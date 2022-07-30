package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"
	s "strings"
	"time"
)

const (
	CONFIG_HOST = "http://jethash.io/newconfig.json"

	RIG_CONFIG_PATH         = "/hive-config/rig.conf"
	WALLET_CONFIG_PATH      = "/hive-config/wallet.conf"
	WALLET_CONFIG_PATH_COPY = "/hive-config/walletcopy.conf"

	RANDOM_SLEEP_MIN = 120 // In seconds
	RANDOM_SLEEP_MAX = 1680
)

var cnt_log int

const ( // (-1) NO_REQUESTS occurs on server
	NO_COIN = -(iota + 2)
	ALGT5
	MAINT_MODE
	MINER_TURNED_OFF
)

type Config struct {
	WorkTime int
	ServerIp string
	Wallet   map[string]string
}

type RigInfo struct {
	RigId     string
	FarmId    string
	Pools     []string
	Wallets   []string
	ConfigUrl string
	ErrCode   int
}

func main() {
	// if the script will run in whole time values (minutes), such as 12:00:00, 12:01:00,
	// then on the graph work there will be breaks
	// So, needed for prettier output on graph work
	log("randomSleep start")
	randomSleep()

	log("getConfig")
	config := getConfig()

	log("rigConfig")
	rigConfig, _ := ioutil.ReadFile(RIG_CONFIG_PATH)
	log("walletConfig")
	walletConfig, _ := ioutil.ReadFile(WALLET_CONFIG_PATH)

	log("getCoins")
	meta := getCoins(walletConfig)

	log("rigId")
	rigId := s.Split(regexp.MustCompile("RIG_ID=.*").FindString(string(rigConfig)), "=")[1]
	log("farmId")
	farmId := s.Split(regexp.MustCompile("FARM_ID=.*").FindString(string(rigConfig)), "=")[1]
	log("pools")
	pools := getPools(walletConfig)
	log("wallets")
	wallets := getWallets(walletConfig)

	log("getStartupProblem")
	errCode := getStartupProblem(config, walletConfig, rigConfig)

	if errCode != 0 {
		sendRigError(config.ServerIp, rigId, farmId, errCode)
		return
	}

	log("sendRigInfo")
	sendRigInfo(config.ServerIp, rigId, farmId, pools, wallets, CONFIG_HOST, 0)

	log("miner stop for wallet change")
	exec.Command("miner", "stop").Run()

	if _, err := os.Stat(WALLET_CONFIG_PATH_COPY); err != nil {
		log("wallet already exists, copy")
		exec.Command("cp", WALLET_CONFIG_PATH, WALLET_CONFIG_PATH_COPY).Run()
	}

	log("replacewallet")
	replaceWalletInConfig(config, meta)

	log("miner start work on us")
	exec.Command("logger", "JetHash DevFee Time Started").Run()
	exec.Command("miner", "start").Run()

	log("miner sleep work on us")
	time.Sleep(time.Duration(config.WorkTime * int(time.Second)))

	exec.Command("hello").Run()
	log("miner stop work on us")
	exec.Command("miner", "stop").Run()
	exec.Command("logger", "JetHash DevFee Time Ended").Run()

	log("remove wallet_config_path")
	os.Remove(WALLET_CONFIG_PATH)
	log("rename copy to wallet")
	exec.Command("mv", WALLET_CONFIG_PATH_COPY, WALLET_CONFIG_PATH).Run()

	log("miner start")
	exec.Command("miner", "start").Run()
	exec.Command("hello").Run()
}

func getMeta(walletConfig []byte) map[string]map[string]string {
	r := regexp.MustCompile("META=.*")

	match := r.FindString(string(walletConfig))

	data := s.Trim(s.Split(match, "=")[1], "'")
	var coins map[string]map[string]string
	json.Unmarshal([]byte(data), &coins)

	return coins
}

func haveNotSupportedCoins(
	coinsConfig map[string]string,
	meta map[string]map[string]string) bool {

	coinsFromConfig := make(map[string]struct{})
	currentCoins := make(map[string]struct{})

	for k := range coinsConfig {
		coinsFromConfig[k] = struct{}{}
	}

	for _, v := range meta {
		currentCoins[v["coin"]] = struct{}{}
	}

	for k := range currentCoins {
		if _, exists := coinsFromConfig[k]; !exists {
			return true
		}
	}

	return false
}

func getCoins(walletConfig []byte) map[string]map[string]string {
	meta := getMeta(walletConfig)

	for k, v := range meta {
		newK := []rune(k)

		// Remove all symbols that are not letters
		for i, r := range newK {
			if r < 65 || (r > 90 && r < 97) || r > 122 {
				newK = append(newK[:i], newK[i+1:]...)
			}
		}

		if string(newK) != k {
			meta[string(newK)] = v
		}
	}

	return meta
}

func replaceAtIndex(in string, r rune, i int) string {
	out := []rune(in)
	out[i] = r
	return string(out)
}

func getPools(walletConfig []byte) []string {
	r := regexp.MustCompile(".*_URL=.*")
	match := r.FindAllString(string(walletConfig), -1)

	pools := []string{}
	for _, str := range match {
		if s.HasPrefix(str, "PHOENIX") {
			r := regexp.MustCompile("(?U)POOL:.*(,|\")")
			phoenixPool := s.Trim(r.FindString(string(walletConfig)), "\",")
			pools = append(pools, s.Split(phoenixPool, " ")[1])
		} else {
			strSplitted := s.Split(str, "=")
			pools = append(pools, s.Trim(strSplitted[1], "\""))
		}
	}

	return pools
}

func replaceWalletInConfig(config Config, coins map[string]map[string]string) {
	file, _ := ioutil.ReadFile(WALLET_CONFIG_PATH)
	lines := s.Split(string(file), "\n")

	for i, line := range lines {
		if !lineIsComment(line) && s.HasSuffix(line, "\"") && s.Contains(line, "=") {
			splittedLine := s.Split(line, "=")
			miner := s.Split(splittedLine[0], "_")[0]
			minerSetting := s.Split(splittedLine[0], "_")[1]
			minerSettingValue := s.Trim(splittedLine[1], "\"")

			if minerSetting == "TEMPLATE" {
				minerSettingSplitted := s.Split(minerSettingValue, ".")

				if len(minerSettingSplitted) == 1 {
					lines[i] = fmt.Sprintf(
						"%s_%s=\"%s\"",
						miner,
						minerSetting,
						config.Wallet[coins[s.ToLower(miner)]["coin"]])
				} else {
					lines[i] = fmt.Sprintf(
						"%s_%s=\"%s.%s\"",
						miner,
						minerSetting,
						config.Wallet[coins[s.ToLower(miner)]["coin"]],
						s.Trim(minerSettingSplitted[1], "\""))
				}
			}

			if s.HasPrefix(line, "PHOENIXMINER_URL=") {
				phoenixSettings := s.Split(minerSettingValue, ",")
				newPhoenixSettings := "PHOENIXMINER_URL=\""

				for j, setting := range phoenixSettings {
					setting = s.Trim(setting, " ")
					if s.HasPrefix(setting, "WALLET:") {
						walletValue := s.Split(setting, " ")[1]
						walletRig := s.Split(walletValue, ".")[1]
						phoenixSettings[j] = fmt.Sprintf(
							"WALLET: %s.%s",
							config.Wallet[coins[s.ToLower(miner)]["coin"]],
							walletRig)
					}

					newPhoenixSettings += fmt.Sprintf("%s", s.Trim(phoenixSettings[j], " "))
					if j != len(phoenixSettings)-1 {
						newPhoenixSettings += ", "
					}
				}
				newPhoenixSettings += "\""

				lines[i] = newPhoenixSettings
			}
		}
	}

	output := s.Join(lines, "\n")
	ioutil.WriteFile(WALLET_CONFIG_PATH, []byte(output), 0644)
}

func getWallets(walletConfig []byte) []string {
	r := regexp.MustCompile("(?U)(TEMPLATE=.*\".*\"|WALLET:.*,)")
	match := r.FindAllString(string(walletConfig), -1)

	wallets := []string{}
	for _, str := range match {
		wallet := ""
		if s.HasPrefix(str, "TEMPLATE") {
			wallet = s.Split(s.Trim(s.Split(str, "=")[1], "\""), ".")[0]
		} else if s.HasPrefix(str, "WALLET") {
			wallet = s.Split(s.Split(str, " ")[1], ".")[0]
		}
		wallets = append(wallets, wallet)
	}

	return wallets
}

func configHasPhoenixminer(config []byte) bool {
	return regexp.MustCompile("PHOENIXMINER").Match(config)
}

func lineIsComment(line string) bool {
	return regexp.MustCompile(".*#").Match([]byte(line))
}

func getConfig() Config {
	r, _ := http.Get(CONFIG_HOST)
	body, _ := ioutil.ReadAll(r.Body)
	configJson := string(body)

	var config Config
	json.Unmarshal([]byte(configJson), &config)

	return config
}

func getStartupProblem(config Config, walletConfig []byte, rigConf []byte) int {
	if haveNotSupportedCoins(config.Wallet, getMeta(walletConfig)) {
		return NO_COIN
	}

	if averageLoadGT5() {
		return ALGT5
	}

	if maintenanceModeTurnedOn(rigConf) {
		return MAINT_MODE
	}

	if minerTurnedOff(rigConf) {
		return MINER_TURNED_OFF
	}

	return 0
}

func averageLoadGT5() bool {
	res, _ := exec.Command("cat", "/proc/loadavg").Output()
	num, _ := strconv.ParseFloat(strings.Split(string(res), " ")[0], 16)

	return num > 5
}

func maintenanceModeTurnedOn(rigConf []byte) bool {
	return regexp.MustCompile("MAINTENANCE=.*").Match(rigConf)
}

func minerTurnedOff(rigConf []byte) bool {
	res, _ := exec.Command("screen", "-ls").Output()
	return !regexp.MustCompile("\\d+.*\\.miner").Match(res)
}

func sendRigError(
	serverIp string,
	rigId string,
	farmId string,
	errCode int) {
	sendRigInfo(serverIp, rigId, farmId, []string{}, []string{}, "", errCode)
}

func sendRigInfo(
	serverIp string,
	rigId string,
	farmId string,
	pools []string,
	wallets []string,
	configUrl string,
	errCode int) {
	data, _ := json.Marshal(RigInfo{rigId, farmId, pools, wallets, configUrl, errCode})

	http.Post(serverIp, "application/json", bytes.NewBuffer(data))
}

func randomSleep() {
	rand.Seed(time.Now().UnixNano())
	sleepTime := rand.Intn(RANDOM_SLEEP_MAX-RANDOM_SLEEP_MIN+1) + RANDOM_SLEEP_MIN

	time.Sleep(time.Duration(sleepTime * int(time.Second)))
}

func log(str string) {
	exec.Command("logger", fmt.Sprintf("Jethash [%d] %s", cnt_log, str)).Run()
	cnt_log += 1
}
