import jpype
import asposecells
jpype.startJVM()
from asposecells.api import *
import json

MAIN = 'mainPrice'

CHARS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']

items = json.loads(open('../dataset.json', 'r').read())
column_names = [key for key in items[0]['vars'].keys()]

result = Workbook(FileFormatType.XLSX)
table = result.getWorksheets().get(0).getCells()
i=1
for column_name in column_names:
    if column_name == MAIN:
        continue
    table.get(CHARS[i] + '1').putValue(column_name)
    i += 1
table.get('A1').putValue(MAIN)

for i, item in enumerate(items):
    table.get('A' + str(i+2)).putValue(item['vars'][MAIN])
    ii = 2
    for column_name in column_names:
        if column_name == MAIN:
            continue
        table.get(CHARS[ii-1] + str(i+2)).putValue(item['vars'][column_name])
        ii += 1 

result.save('../data.xlsx')
