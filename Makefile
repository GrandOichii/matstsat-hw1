all:
	@cd price-scraper/;go run .;cd ..

all1:
	@python3 main.py
	@cat result.tex | pbcopy

.DEFAULT_GOAL=all