package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/GrandOichii/colorwrapper"
	"github.com/go-rod/rod"
	"github.com/go-rod/rod/lib/launcher"
	"github.com/go-rod/rod/lib/proto"
)

// Двухкомнатные квартиры взяты с сайта https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=%d&region=1&room2=1
// Центральные районы Москвы взяты с сайта https://puls-msk.ru/centr-moskvy/
// Станции метро районов москвы взяты с сайта https://ru.wikipedia.org

// Расстояние от центра до станции метро

const (
	startPage = 18
	endPage   = 30

	URL = "https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=%d&region=1&room2=1"

	cardSelector      = "div[data-name=\"LinkArea\"]"
	titleSelector     = "span[data-mark=\"OfferTitle\"]"
	subtitleSelector  = "span[data-mark=\"OfferSubtitle\"]"
	geoSelector       = "div[data-name=\"SpecialGeo\"]"
	mainPriceSelector = "span[data-mark=\"MainPrice\"]"
	priceInfoSelector = "p[data-mark=\"PriceInfo\"]"
	stationSelector   = ".a10a3f92e9--underground_link--Sxo7K"
)

var ignoreList = []string{
	"https://www.cian.ru/sale/flat/271547026/",
	"https://www.cian.ru/sale/flat/271704920/",
	"https://www.cian.ru/sale/flat/269222371/",
	"https://www.cian.ru/sale/flat/272566535/",
	"https://www.cian.ru/sale/flat/273637601/",
	"https://www.cian.ru/sale/flat/270817751/",
	"https://www.cian.ru/sale/flat/272532068/",
	"https://www.cian.ru/sale/flat/271222341/",
	"https://www.cian.ru/sale/flat/273717818/",
	"https://www.cian.ru/sale/flat/273578888/",
	"https://www.cian.ru/sale/flat/272575953/",
	"https://www.cian.ru/sale/flat/269019912/",
	"https://www.cian.ru/sale/flat/272329175/",
	"https://www.cian.ru/sale/flat/271034921/",
	"https://www.cian.ru/sale/flat/273316215/",
	"https://www.cian.ru/sale/flat/271161220/",
}

func ignoreThis(link string) bool {
	for _, ign := range ignoreList {
		if ign == link {
			return true
		}
	}
	return false
}

var centralStations = []string{
	"Красные Ворота",
	"Чистые пруды",
	"Лубянка",
	"Бауманская",
	"Курская",
	"Китай-город",
	"Чкаловская",
	"Электрозаводская",
	"Арбатская",
	"Смоленская",
	"Библиотека имени Ленина",
	"Александровский сад",
	"Боровицкая",
	"Новокузнецкая",
	"Павелецкая",
	"Добрынинская",
	"Третьяковская",
	"Серпуховская",
	"Красносельская",
	"Комсомольская",
	"Чистые пруды",
	"Комсомольская",
	"Сухаревская",
	"Тургеневская",
	"Сретенский бульвар",
	"Лубянка",
	"Рижская",
	"Проспект Мира",
	"Сухаревская",
	"Кузнецкий Мост",
	"Трубная",
	"Международная",
	"Выставочная",
	"Краснопресненская",
	"Беговая",
	"Улица 1905 года",
	"Баррикадная",
	"Деловой центр",
	"Деловой центр",
	"Шелепиха",
	"Деловой центр",
	"Шелепиха",
	"Тестовская",
	"Беговая",
	"Таганская",
	"Китай-город",
	"Китай-город",
	"Таганская",
	"Пролетарская",
	"Площадь Ильича",
	"Марксистская",
	"Крестьянская застава",
	"Лубянка",
	"Охотный Ряд",
	"Библиотека имени Ленина",
	"Белорусская",
	"Маяковская",
	"Тверская",
	"Театральная",
	"Площадь Революции",
	"Арбатская",
	"Александровский сад",
	"Белорусская",
	"Новослободская",
	"Суворовская",
	"Китай-город",
	"Пушкинская",
	"Китай-город",
	"Менделеевская",
	"Цветной бульвар",
	"Чеховская",
	"Боровицкая",
	"Достоевская",
	"Кропоткинская",
	"Парк культуры",
	"Фрунзенская",
	"Спортивная",
	"Воробьёвы горы",
	"Парк культуры",
	"Лужники",
	"Полянка",
}

func IsCentralStation(station string) bool {
	for _, s := range centralStations {
		if s == station {
			return true
		}
	}
	return false
}

func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}

func initBrowser() (*rod.Browser, error) {
	u := launcher.New().
		// Set("--blink-settings=imagesEnabled=false").
		// Headless(false).
		MustLaunch()

	result := rod.New().ControlURL(u)
	err := result.Connect()
	if err != nil {
		return nil, err
	}
	return result, nil
}

type BaseVars struct {
	Square             float64 `json:"square"`
	LiveSquare         int     `json:"liveSquare"`
	IsFirstOrLastFloor int     `json:"isFirstOrLastFloor"`
	MaxFloor           float64 `json:"maxFloor"`
	ToMetro            float64 `json:"toMetro"`
	MainPrice          int     `json:"mainPrice"`
	Year               int     `json:"yearOfConstructuon"`
	HasElevator        int     `json:"hasElevator"`
	Type               int     `json:"isNovostroyka"`
}

func (v BaseVars) print() {
	fmt.Printf("Square: %f\tNumber of floors: %v\tIs first or last floor: %v\tTo metro: %v\tPrice: %v\tHas elevator: %v\tLive square: %v\n", v.Square, v.MaxFloor, v.IsFirstOrLastFloor, v.ToMetro, v.MainPrice, v.HasElevator, v.LiveSquare)
}

type ChowVars struct {
	IsNearCentralStation bool
}

func (c ChowVars) print() {
	fmt.Printf("Is near center: %v\n", c.IsNearCentralStation)
}

type FlatData struct {
	Vars BaseVars `json:"vars"`
	Chow ChowVars `json:"chowVars"`
}

func (f FlatData) print() {
	f.Vars.print()
	f.Chow.print()
}

// func (f *FlatData) inject(line string) error {
// 	origLine := line
// 	line = strings.TrimPrefix(line, "2-комн. ")
// 	line = strings.TrimPrefix(line, "кв., ")
// 	line = strings.TrimPrefix(line, "апарт., ")
// 	i := strings.Index(line, " ")
// 	if i == -1 {
// 		return fmt.Errorf("can't inject line %s - no space for square", origLine)
// 	}
// 	// set the square
// 	square, err := strconv.ParseFloat(strings.ReplaceAll(line[:i], ",", "."), 64)
// 	if err != nil {
// 		return err
// 	}
// 	f.Vars.Square = square

// 	// set the floors
// 	line = line[i+7:]
// 	line = strings.TrimSuffix(line, " этаж")
// 	floors := strings.Split(line, "/")
// 	f.Vars.Floor, err = strconv.Atoi(floors[0])
// 	if err != nil {
// 		return err
// 	}
// 	f.Vars.MaxFloor, err = strconv.Atoi(floors[1])
// 	if err != nil {
// 		return err
// 	}
// 	return nil
// }

func main() {
	browser, err := initBrowser()
	checkErr(err)
	defer browser.Close()

	count := 0
	fds := []*FlatData{}
	page, err := browser.Page(proto.TargetCreateTarget{})
	defer page.Close()
	checkErr(err)
	for i := startPage; i <= endPage; i++ {
		waitFunc := page.MustWaitNavigation()

		colorwrapper.Printf("cyan", "Accessing page #%d\n", i)
		err = page.Navigate(fmt.Sprintf(URL, i))
		checkErr(err)
		waitFunc()

		page.Mouse.Scroll(0, 100, 2)

		els := page.MustElements(cardSelector)
		fmt.Printf("Found cards: %d\n", len(els))
		for _, el := range els {
			link, err := el.Element("._93444fe79c--link--eoxce")
			checkErr(err)
			text, err := link.Attribute("href")
			checkErr(err)
			if ignoreThis(*text) {
				continue
			}
			fd, err := extractFlatData(browser, *text)
			if err != nil {
				colorwrapper.Printf("red", "Failed to fetch info from %s\n", *text)
			} else {
				fds = append(fds, fd)
				colorwrapper.Printf("green", "Extracted info from %s\n", *text)
				// fd.print()
				count++
			}
		}
		data, err := json.MarshalIndent(fds, "", "\t")
		checkErr(err)
		err = os.WriteFile("../price-data.json", data, 0755)
		checkErr(err)
	}
	data, err := json.MarshalIndent(fds, "", "\t")
	checkErr(err)
	fmt.Printf("Counted: %d\n", count)
	err = os.WriteFile("../price-data.json", data, 0755)
	checkErr(err)
	colorwrapper.Println("green", "Saved!")
}

func extractFlatData(browser *rod.Browser, link string) (*FlatData, error) {
	fmt.Printf("\tLooking at page %s\n", link)
	page, err := browser.Page(proto.TargetCreateTarget{})
	waitFunc := page.MustWaitNavigation()
	err = page.Navigate(link)
	checkErr(err)
	waitFunc()
	defer page.Close()

	result := FlatData{}
	// metro and time
	metro, time, err := getStation(page)
	if err != nil {
		return nil, err
	}
	colorwrapper.Printf("cyan", "\tExtracted metro\n")
	result.Chow.IsNearCentralStation = IsCentralStation(metro)
	result.Vars.ToMetro = time
	// square
	result.Vars.Square, err = getSquare(page)
	if err != nil {
		return nil, err
	}
	colorwrapper.Printf("cyan", "\tExtracted square\n")
	// floor data
	var floor float64
	floor, result.Vars.MaxFloor, err = extractFloorData(page)
	if err != nil {
		return nil, err
	}
	colorwrapper.Printf("cyan", "\tExtracted floor\n")
	result.Vars.IsFirstOrLastFloor = 0
	if floor == 0 || floor == result.Vars.MaxFloor {
		result.Vars.IsFirstOrLastFloor = 1
	}
	if err != nil {
		return nil, err
	}
	// price
	f, err := extractPrice(page)
	if err != nil {
		return nil, err
	}
	colorwrapper.Printf("cyan", "\tExtracted price\n")
	result.Vars.MainPrice = int(f)
	result.Vars.Year, err = extractYear(page)
	if err != nil {
		return nil, err
	}
	colorwrapper.Printf("cyan", "\tExtracted year\n")
	result.Vars.HasElevator = 0
	if result.Vars.MaxFloor > 5 {
		result.Vars.HasElevator = 1
	}
	sq, err := extractLiveSquare(page)
	if err != nil {
		return nil, err
	}
	colorwrapper.Printf("cyan", "\tExtracted live square\n")
	result.Vars.LiveSquare = sq
	result.Vars.Type, err = extractType(page)
	if err != nil {
		return nil, err
	}
	colorwrapper.Printf("cyan", "\tExtracted type\n")
	return &result, nil
}

func extractLiveSquare(page *rod.Page) (int, error) {
	els, err := page.Elements("div[class=\"a10a3f92e9--info-title--JWtIm\"]")
	if err != nil {
		return 0, err
	}
	for _, el := range els {
		text, err := el.Text()
		if err != nil {
			return 0, err
		}
		if strings.Contains(text, "Жилая") {
			prev, err := el.Previous()
			if err != nil {
				return 0, err
			}
			t, err := prev.Text()
			if err != nil {
				return 0, err
			}
			f, err := extractFloat(t)
			if err != nil {
				return 0, err
			}
			return int(f), nil
		}
	}
	return 0, errors.New("can't get live space")
}

func extractYear(page *rod.Page) (int, error) {
	els, err := page.Elements("div[class=\"a10a3f92e9--info-title--JWtIm\"]")
	if err != nil {
		return 0, err
	}
	for _, el := range els {
		text, err := el.Text()
		if err != nil {
			return 0, err
		}
		if text == "Построен" {
			prev, err := el.Previous()
			if err != nil {
				return 0, err
			}
			t, err := prev.Text()
			if err != nil {
				return 0, err
			}
			f, err := extractFloat(t)
			if err != nil {
				return 0, err
			}
			return int(f), nil
		}
		if text == "Срок сдачи" {
			prev, err := el.Previous()
			if err != nil {
				return 0, err
			}
			t, err := prev.Text()
			if err != nil {
				return 0, err
			}
			f, err := extractFloat(t[len(t)-4:])
			if err != nil {
				return 0, err
			}
			return int(f), nil
		}
		if text == "Сдан" {
			prev, err := el.Previous()
			if err != nil {
				return 0, err
			}
			t, err := prev.Text()
			if err != nil {
				return 0, err
			}
			f, err := extractFloat(t[len(t)-4:])
			if err != nil {
				return 0, err
			}
			return int(f), nil
		}
	}
	return 0, errors.New("can't get date of construction")
}

func extractFloorData(page *rod.Page) (float64, float64, error) {
	els, err := page.Elements("div[data-testid=\"object-summary-description-value\"]")
	if err != nil {
		return 0, 0, err
	}
	for _, el := range els {
		text, err := el.Text()
		if err != nil {
			return 0, 0, err
		}
		if strings.Contains(text, " из ") {
			split := strings.Split(text, " из ")
			result1, err := extractFloat(split[0])
			if err != nil {
				return 0, 0, err
			}
			result2, err := extractFloat(split[1])
			if err != nil {
				return 0, 0, err
			}
			return result1, result2, nil
		}
	}
	return 0, 0, fmt.Errorf("no floor data found")
}

func extractPrice(page *rod.Page) (float64, error) {
	el, err := page.Element("span[itemprop=\"price\"]")
	if err != nil {
		return 0, err
	}
	text, err := el.Text()
	if err != nil {
		return 0, err
	}
	return extractFloat(text)
}

func getSquare(page *rod.Page) (float64, error) {
	el, err := page.Element(".a10a3f92e9--info-value--bm3DC")
	if err != nil {
		return 0, err
	}
	text, err := el.Text()
	if err != nil {
		return 0, err
	}
	return extractFloat(text)
}

func getStation(page *rod.Page) (string, float64, error) {
	st, err := page.Element(stationSelector)
	if err != nil {
		return "", 0, err
	}
	result1, err := st.Text()
	if err != nil {
		return "", 0, err
	}
	st, err = st.Next()
	if err != nil {
		return "", 0, err
	}
	text, err := st.Text()
	if err != nil {
		return "", 0, err
	}
	result2, err := extractFloat(text)
	if err != nil {
		return "", 0, err
	}
	return result1, result2, err
}

func getPrices(el *rod.Element) (int, int, error) {
	mainPrice, err := el.Element(mainPriceSelector)
	if err != nil {
		return 0, 0, err
	}
	text, err := mainPrice.Text()
	if err != nil {
		return 0, 0, err
	}
	text = strings.ReplaceAll(text, " ", "")
	text = strings.ReplaceAll(text, "₽", "")
	text = strings.ReplaceAll(text, "\u00a0", "")
	result1, err := strconv.Atoi(text)
	if err != nil {
		return 0, 0, err
	}

	priceInfo, err := el.Element(priceInfoSelector)
	if err != nil {
		return 0, 0, err
	}
	text, err = priceInfo.Text()
	if err != nil {
		return 0, 0, err
	}
	text = strings.ReplaceAll(text, " ", "")
	text = strings.ReplaceAll(text, "\u00a0₽/м²", "")
	result2, err := strconv.Atoi(text)
	if err != nil {
		return 0, 0, err
	}
	return result1, result2, nil
}

func extractFloat(line string) (float64, error) {
	ntext := ""
	nums := []string{"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", ","}
	sp := strings.Split(line, "")
	for _, c := range sp {
		for _, n := range nums {
			if c == n {
				ntext += c
				break
			}
		}
	}
	ntext = strings.ReplaceAll(ntext, ",", ".")
	return strconv.ParseFloat(ntext, 64)
}

func extractType(page *rod.Page) (int, error) {
	els, err := page.Elements(".a10a3f92e9--name--x7_lt")
	if err != nil {
		return 0, err
	}
	for _, el := range els {
		text, err := el.Text()
		if err != nil {
			return 0, err
		}
		if text == "Тип жилья" {
			next, err := el.Next()
			if err != nil {
				return 0, err
			}
			t, err := next.Text()
			if err != nil {
				return 0, err
			}
			result := 0
			if t == "Новостройка" {
				result = 1
			}
			return result, nil
		}
	}
	return 0, errors.New("failed to extract type")
}
