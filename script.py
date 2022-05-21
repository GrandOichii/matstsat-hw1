# random value adder
# import json
# from random import randint

# path = 'price-data2.json'

# items = json.loads(open(path, 'r').read())
# for item in items:
#     item['chowVars']['randValue'] = randint(0, 1) == 0
# open(path, 'w').write(json.dumps(items, indent=4, sort_keys=True))

# excel reader
# import json
# import pandas as pd

# xls = pd.ExcelFile('table.xlsx')

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

# duplicate finder
import json
items = json.loads(open('price-data-final1-19.json', 'r').read())
for i in range(len(items)-1):
    item = items[i]
    for j in range(i+1, len(items)):
        citem = items[j]
        if item['vars']['mainPrice'] == citem['vars']['mainPrice']:
            if item['vars']['square'] == citem['vars']['square'] and item['vars']['maxFloor'] == citem['vars']['maxFloor']:
                    print('found duplicate - ', item['vars']['mainPrice'])