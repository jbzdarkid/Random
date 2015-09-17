def nCr(n, r):
	arr = []
	for i in range(r):
		arr.append(i)
	yield arr
	
	i = size-1
	while i >= 0:
		arr[i] += 1
		while i < size - 1:
			i += 1
			arr[i] = arr[i-1] + 1
		yield arr
		while arr[i] < n-1:
			arr[i] += 1
			yield arr
		while arr[i] == n + i - r:
			i -= 1
