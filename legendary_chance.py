# If you open two legendaries in one pack, this will call that 'distance 0'

from urllib2 import urlopen
from csv import reader

firstRow = True
fileId = None
packId = None
counts = []

firstOnly = True

buffer = ''

for row in reader(urlopen('http://gist.githubusercontent.com/jleclanche/9d3cfa115a2deec6b759/raw/2806438a31f85d4251eafa544e6544b762e35941/export.csv', 'rb')):
	if firstRow:
		firstRow = False
		continue
	buffer += ', '.join(row) + '\n'
	if row[0] != fileId:
		fileId = row[0]
		foundLegendary = False
		count = 0
	if row[1] != packId:
		count += 1
		packId = row[1]
	if row[6] =='LEGENDARY':
		if firstOnly and foundLegendary:
			continue
		foundLegendary = True
		counts.append(count)
		count = 0

for i in range(min(counts), max(counts)+1):
	print '%2d' % i, '*'*counts.count(i)