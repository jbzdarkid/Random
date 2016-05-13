def nCr(n, r):
	arr = []
	for i in range(r):
		arr.append(i)
	yield arr
	if r == n:
		return

	i = r-1
	while i >= 0:
		arr[i] += 1
		while i < r-1:
			i += 1
			arr[i] = arr[i-1] + 1
		yield arr
		while arr[i] < n-1:
			arr[i] += 1
			yield arr
		while arr[i] == n + i - r:
			i -= 1

def nPr(n, r):
	for set in nCr(n, r):
		for p in permute(set):
			yield p

def permute(set):
	if len(set) == 0:
		yield []
	for elem in set:
		subset = list(set)
		subset.remove(elem)
		for p in permute(subset):
			yield [elem] + p
