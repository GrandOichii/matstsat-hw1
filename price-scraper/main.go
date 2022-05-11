package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/GrandOichii/colorwrapper"
	"github.com/go-rod/rod"
	"github.com/go-rod/rod/lib/launcher"
	"github.com/go-rod/rod/lib/proto"
)

const (
	pages = 20

	URL = "https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=%d&region=1&room2=1"

	cardSelector      = "div[data-name=\"LinkArea\"]"
	titleSelector     = "span[data-mark=\"OfferTitle\"]"
	subtitleSelector  = "span[data-mark=\"OfferSubtitle\"]"
	geoSelector       = "div[data-name=\"SpecialGeo\"]"
	mainPriceSelector = "span[data-mark=\"MainPrice\"]"
	priceInfoSelector = "p[data-mark=\"PriceInfo\"]"
)

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

type FlatData struct {
	Square     float64 `json:"square"`
	Floor      int     `json:"floor"`
	MaxFloor   int     `json:"maxFloor"`
	ToMetro    int     `json:"toMetro"`
	MainPrice  int     `json:"mainPrice"`
	OtherPrice int     `json:"otherPrice"`
}

func (f FlatData) print() {
	fmt.Printf("Square: %f\tFloor: %d/%d\tTo metro: %d\tPrice: %d\tOther price: %d\n", f.Square, f.Floor, f.MaxFloor, f.ToMetro, f.MainPrice, f.OtherPrice)
}

func (f *FlatData) inject(line string) error {
	origLine := line
	line = strings.TrimPrefix(line, "2-комн. ")
	line = strings.TrimPrefix(line, "кв., ")
	line = strings.TrimPrefix(line, "апарт., ")
	i := strings.Index(line, " ")
	if i == -1 {
		return fmt.Errorf("can't inject line %s - no space for square", origLine)
	}
	// set the square
	square, err := strconv.ParseFloat(strings.ReplaceAll(line[:i], ",", "."), 64)
	if err != nil {
		return err
	}
	f.Square = square

	// set the floors
	line = line[i+7:]
	line = strings.TrimSuffix(line, " этаж")
	floors := strings.Split(line, "/")
	f.Floor, err = strconv.Atoi(floors[0])
	if err != nil {
		return err
	}
	f.MaxFloor, err = strconv.Atoi(floors[1])
	if err != nil {
		return err
	}
	return nil
}

func main() {
	browser, err := initBrowser()
	checkErr(err)
	defer browser.Close()

	count := 0
	fds := []*FlatData{}
	page, err := browser.Page(proto.TargetCreateTarget{})
	defer page.Close()
	checkErr(err)
	for i := 1; i <= pages; i++ {
		waitFunc := page.MustWaitNavigation()

		colorwrapper.Printf("cyan", "Accessing page #%d\n", i)
		err = page.Navigate(fmt.Sprintf(URL, i))
		checkErr(err)
		waitFunc()

		page.Mouse.Scroll(0, 100, 2)

		els := page.MustElements(cardSelector)
		fmt.Printf("Found cards: %d\n", len(els))
		for _, el := range els {
			fd := FlatData{}

			titleText := getTitleText(el)
			if titleText == "" {
				colorwrapper.Println("red", "No card info found, ignoring")
				continue
			}
			err = fd.inject(titleText)
			checkErr(err)

			geo, err := getGeo(el)
			if err != nil {
				colorwrapper.Println("red", "Failed to get the minutes ti the metro, ignoring")
				continue
			}
			fd.ToMetro = geo

			fd.MainPrice, fd.OtherPrice, err = getPrices(el)
			checkErr(err)

			fd.print()
			fds = append(fds, &fd)
			count++
		}
	}
	data, err := json.MarshalIndent(fds, "", "\t")
	checkErr(err)
	fmt.Printf("Counted: %d\n", count)
	err = os.WriteFile("../price-data.json", data, 0755)
	checkErr(err)
	colorwrapper.Println("green", "Saved!")
}

func getTitleText(el *rod.Element) string {
	result := ""
	title, err := el.Element(titleSelector)
	if err == nil {
		text := title.MustText()
		if strings.HasPrefix(text, "2-") {
			result = text
		}
	}
	subtitle, err := el.Element(subtitleSelector)
	if err == nil {
		text := subtitle.MustText()
		if strings.HasPrefix(text, "2-") {
			result = text
		}
	}
	return result
}

func getGeo(el *rod.Element) (int, error) {
	geo, err := el.Element(geoSelector)
	if err != nil {
		return 0, err
	}
	text, err := geo.Text()
	origText := text
	if err != nil {
		return 0, err
	}
	sp := strings.Split(text, "\n")
	if len(sp) == 1 {
		return 0, fmt.Errorf("failed to access minutes from %s", origText)
	}
	dist := sp[1]
	i := strings.Index(dist, " ")
	result, err := strconv.Atoi(dist[:i])
	return result, err
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
