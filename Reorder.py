import random
size = 4
factorial = [1] * size
for i in range(1, size):
	factorial[i] = factorial[i-1] * i
print factorial
r = random.randint(0, factorial[size-1])
print 'rand:', r

for i in range(size, 0, -1):
	print r/factorial[i-1]

reorder = [None] * size



o[0] = r%6
o[1] = r


'''
abcd
abdc
acbd
acdb
adbc
adcb
bacb
badc
bcad
bcda
bdac
bdca
cabd
cadb
cbad
cbda
cdab
cdba
da
da
db
db
dc
dc
'''
