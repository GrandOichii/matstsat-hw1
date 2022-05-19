import json
from random import randint

path = 'price-data2.json'

items = json.loads(open(path, 'r').read())
for item in items:
    item['chowVars']['randValue'] = randint(0, 1) == 0
open(path, 'w').write(json.dumps(items, indent=4, sort_keys=True))

# import json
# import pandas as pd

# xls = pd.ExcelFile('table.xlsx') #use r before absolute file path 

# sheetX = xls.parse(0) 

# items = []
# for row in range(0, sheetX.shape[0]):
#     item = {'vars': {}, 'chowVars': {}}
#     for column in sheetX.columns:
#         item['vars'][column] = int(sheetX[column][row])
#     items += [item]
#     print(item)
# print(len(items))
# open('price-data2.json', 'w').write(json.dumps(items, sort_keys=True, indent=4))