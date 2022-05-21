import json

import analisys

DATA_PATH = 'price-data-final1-19.json'

def read_items(path: str):
    with open(path, 'r') as f:
        return json.loads(f.read())

items = read_items(DATA_PATH)
result = analisys.analise(items, 'mainPrice')
result.write_latex_to('result.tex')

# fix the chow test latex reoresentation
# do the correlation tests
# send the question to the professor