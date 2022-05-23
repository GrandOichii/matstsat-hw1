import json

import analisys

DATA_PATH = 'dataset.json'
# DATA_PATH = 'tools/result.json'

def read_items(path: str):
    with open(path, 'r') as f:
        return json.loads(f.read())

items = read_items(DATA_PATH)
result = analisys.analise(items, 'mainPrice')
# result = analisys.analise(items, 'qmor')
result.write_latex_to('result.tex')