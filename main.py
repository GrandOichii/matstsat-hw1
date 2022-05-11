import json
import termcolor

import analisys

DATA_PATH = 'price-data.json'

def read_items(path: str):
    with open(path, 'r') as f:
        return json.loads(f.read())

items = read_items(DATA_PATH)
result = analisys.analise(items, 'mainPrice')
print(result)
result.write_latex_to('result.tex')