scrape:
	@cd price-scraper/;go run .;cd ..

analize:
	@python3 main.py
	@cat result.tex | pbcopy

.DEFAULT_GOAL=analize